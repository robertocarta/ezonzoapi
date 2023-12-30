from fastapi.testclient import TestClient
from app.app import app, get_session, _create_product
from app.database import db_setup
from app.models import Base, Product, Shop
from app.schemas import ShopCreate, ProductCreate
import os
from sqlalchemy.orm import Session
import pytest

from app.schemas import ShopCreate


SHOPS_DATA = (
        {
            'name': 'a',
            'lat': 20,
            'lon': 21,
            'address': 'Via Scano',
            'url': 'www.aexample.com'
            },
        {
            'name': 'b',
            'lat': 20,
            'lon': 22,
            'address': 'Via Saffi',
            'url': 'www.bexample.com'
            },
        {
            'name': 'c',
            'lat': 21,
            'lon': 20,
            'address': 'Via Saffi',
            'url': 'www.bexample.com'
            }
        )

PRODUCTS_DATA = (
        {
            "url": "https://example.it",
            "name": "Product A",
            "price": 50,
            "thumbnail": "",
            "tags": "Tags A",
            },
        {
            "url": "https://example.it",
            "name": "Product B",
            "price": 30,
            "thumbnail": "",
            "tags": "Tags B",
            },
        {
            "url": "https://example.it",
            "name": "Product C",
            "price": 20,
            "thumbnail": "",
            "tags":  "Tags c"
            }
        )



engine, SessionLocal = db_setup('_test')


def tst_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


app.dependency_overrides[get_session] = tst_session
Base.metadata.create_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def test_data():
    shops = [ShopCreate(**shop_data) for shop_data in SHOPS_DATA]
    products = [
            ProductCreate(**product, shop=shop)
            for shop in shops
            for product in PRODUCTS_DATA
            ]
    return shops, products


@pytest.fixture(autouse=True)
def setup_and_teardown():
    yield Base.metadata.create_all(bind=engine)  # Create tables
    Base.metadata.drop_all(bind=engine)


def test_shop_get_or_create(session: Session):
    shop_data = {
            'name': 'Shop Name',
            'lat': 10,
            'lon': 20,
            'address': 'Via Scano 3',
            'url':  'https://www.example.com'
            }
    shop_data_obj = ShopCreate(**shop_data)
    new_shop = Shop.get_or_create(session, shop_data_obj)
    new_shop_found = session.query(Shop).filter(Shop.id == new_shop.id).first()
    assert new_shop_found

def test_create_product_stores_data(session, test_data):
    shops, products = test_data

    for product in products:
        _create_product(product, session=session)

    shops_found = session.query(Shop).filter().all()
    products_found = session.query(Product).filter().all()
    assert len(shops_found) == len(shops)
    assert len(products_found) == len(products)

def test_create_product_returns_obj_data(client):
    product_data = dict(PRODUCTS_DATA[0])
    body = dict(product_data)
    body['shop'] = SHOPS_DATA[0]
    response = client.post("/products/", json=body)

    assert response.status_code == 201
    assert response.json() == {**product_data, 'id': 1, 'shopid': 1}






    # products = [
    #         (f'prod_{i}', 'www.example.com', 10, 'www.example.com', 'tags_i')
    #         for i in range(10)
    #         ]
    # products = 
    # for product in 
    #
    #     body = {
    #             "url": mongo_doc['url'],
    #             "name": mongo_doc['title'],
    #             "price": mongo_doc['price'],
    #             "thumbnail": mongo_doc['thumbnail'],
    #             "tags": mongo_doc['thumbnail'],
    #             "shop": {
    #                 "name": mongo_doc['shop'],
    #                 "lat": 44.491189334186075,
    #                 "lon": 11.346369127270156,
    #                 "address": "Via Castiglione, 11 A, 40124 Bologna BO",
    #                 "url": "https://giocheria.it/"
    #                 }
    #             }
    #     resp = requests.post("http://127.0.0.1:8000/products/", json=body)
    #
    # pass
