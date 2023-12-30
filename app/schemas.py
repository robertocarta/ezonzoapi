from typing import List
from pydantic import BaseModel
from datetime import date






class ShopCreate(BaseModel):
    name: str
    lat: float
    lon: float
    address: str
    url: str



class ProductBase(BaseModel):
    id: int
    name: str
    price: float
    thumbnail: str
    tags: str
    shopid: int
    url: str

    class Config:
        orm_mode = True

class ProductCreate(BaseModel):
    url: str
    name: str
    price: float
    thumbnail: str
    tags: str
    shop: ShopCreate


