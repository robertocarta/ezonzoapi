from pydantic import BaseModel


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
    model_config = {
            'from_attributes': True
            }


class ProductCreate(BaseModel):
    url: str
    name: str
    price: float
    thumbnail: str
    tags: str
    shop: ShopCreate
