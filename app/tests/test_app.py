from fastapi.testclient import TestClient
from app.app import app, get_session
from app.database import db_setup
from app.models import Base, Product, Shop
from app.schemas import ShopCreate
import os
from sqlalchemy.orm import Session
import pytest

from app.schemas import ShopCreate


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


def test_create_product_returns_obj_data(client):
    # Define test data
    test_data = {
        "url": "https://example.com/product",
        "name": "Test Product",
        "price": 19.99,
        "thumbnail": "https://example.com/thumbnail.jpg",
        "tags": "one two three four",
        "shop": {
            "name": "Test Shop",
            "lat": 40.7128,
            "lon": -74.0060,
            "address": "Test Address",
            "url": "https://example.com/shop",
        },
    }

    response = client.post("/products/", json=test_data)

    # Assert the response status code
    assert response.status_code == 201

    expected_response = {
        "id": 1,
        "name": "Test Product",
        "price": 19.99,
        "thumbnail": "https://example.com/thumbnail.jpg",
        "tags": "one two three four",
        "shopid": 1,
    }

    assert response.json() == expected_response

