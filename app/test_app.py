from fastapi.testclient import TestClient
from app import app, get_session, _create_product, _get_products
from database import db_setup
from models import Base, Product, Shop
from schemas import ShopCreate, ProductCreate
from sqlalchemy.orm import Session
import pytest


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
            "name": "Product X A",
            "price": 50,
            "thumbnail": "",
            "tags": "Tags A",
            },
        {
            "url": "https://example.it",
            "name": "Product X B",
            "price": 30,
            "thumbnail": "",
            "tags": "Tags B",
            },
        {
            "url": "https://example.it",
            "name": "Product Y C",
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

#
def test__get_products_returns_correct_data(session: Session, test_data):
    # populate database
    test_create_product_stores_data(session, test_data)
    shops, products = test_data
    target_shop = shops[0]
    res = _get_products('Product',
                        target_shop.lat,
                        target_shop.lon,
                        0.01,
                        30,
                        session)
    products = [
            product for product, shop in
            session.query(Product, Shop).join( Shop, Shop.id == Product.shopid ).all()
            if (
                product.price <= 30 and
                'Product' in product.name and
                shop.lat == target_shop.lat and
                shop.lon == target_shop.lon)
            ]
    assert len(res) == len(products)
