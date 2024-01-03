import os
from typing import List
from sqlalchemy import text, func
from fastapi import FastAPI, Depends, Query
from mangum import Mangum

from database import db_setup
from schemas import ProductCreate, ProductBase
from models import Base, Shop, Product, Session


stage = '/dev' if "AWS_LAMBDA_FUNCTION_NAME" in os.environ else '/'
app = FastAPI(openapi_prefix=stage)
handler = Mangum(app, api_gateway_base_path=stage)

engine, SessionLocal = db_setup()
Base.metadata.create_all(bind=engine)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def _create_product(product_data: ProductCreate, session: Session):
    shop = Shop.get_or_create(session, product_data.shop)
    del product_data.shop
    new_product = Product(**product_data.dict(), shopid=shop.id)
    session.add(new_product)
    session.commit()
    session.refresh(new_product)
    return new_product


@app.post("/products/", response_model=ProductBase, status_code=201)
def create_product(product_data: ProductCreate,
                   session: Session = Depends(get_session)):
    return _create_product(product_data, session)


def _get_products(
        search_str: str,
        lat: float,
        lon: float,
        max_distance: float,
        max_price: float,
        session: Session
        ):
    clauses = []
    if max_price is not None:
        clauses.append(Product.price <= max_price)
    clauses.append(Product.name.ilike(f"%{search_str}%"))
    user_location = text(f'ST_SetSRID(ST_MakePoint({lat}, {lon}), 4326)')
    # user_location = text(f'ST_SetSRID(ST_MakePoint({lat}, {lon}), 4326)::geography')
    shops_within_radius = session.query(Shop).filter(
        func.ST_DWithin(
            Shop.location,
            user_location,
            max_distance
        )
    ).all()
    clauses.append(Product.shopid.in_(shop.id for shop in shops_within_radius))
    return session.query(Product).filter(*clauses).all()


@app.get("/products/", response_model=List[ProductBase], status_code=200)
def get_products(
        search_str: str = Query(..., title="search keywords", min_length=2),
        lat: float = Query(..., title="Latitude of the user", ge=-90, le=90),
        lon: float = Query(..., title="Longitude of the user", ge=-180, le=180),
        max_distance: float = Query(..., title="Maximum distance in km", gt=0, lt=100),
        max_price: int = Query(None, title="Maximum price"),
        # setting maximum allowed max_distance to 100 as this is supposed to be for a city
        session: Session = Depends((get_session))
        ):
    return _get_products(search_str, lat, lon, max_distance, max_price, session)
