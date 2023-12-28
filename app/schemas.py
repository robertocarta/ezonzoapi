from typing import List
from pydantic import BaseModel
from datetime import date


class ProductCreate(BaseModel):
    url: str
    name: str
    price: float
    thumbnail: str
    tags: str
    shop: str

class ShopCreate(BaseModel):
    name: str
    lat: float
    lon: float
    address: str
    url: str
