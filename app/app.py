from fastapi import FastAPI, Depends, Query
from mangum import Mangum
import uvicorn

from app.database import db_setup
from app.schemas import ProductCreate, ProductBase
from app.models import Base, Shop, Product, Session

app = FastAPI()
handler = Mangum(app)


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
def create_product(product_data: ProductCreate, session: Session = Depends(get_session)):
    return _create_product(product_data, session)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)  # type: ignore
