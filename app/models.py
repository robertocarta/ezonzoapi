from sqlalchemy import Column, ForeignKey, Integer, String, Float, Index, text
from sqlalchemy.orm import Session
from geoalchemy2 import Geography, WKTElement
from database import Base
from schemas import ShopCreate


class Shop(Base):
    __tablename__ = 'shop'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    location = Column(Geography(geometry_type='POINT'), nullable=False)
    address = Column(String)
    url = Column(String)

    def __init__(self, *args, **kwargs):
        if kwargs.get('location') is None:
            lat, lon = kwargs['lat'], kwargs['lon']
            kwargs['location'] = WKTElement(f"POINT({lat} {lon})", srid=4326)
        super().__init__(*args, **kwargs)





    @classmethod
    def get_or_create(cls, db: Session, shop_data: ShopCreate):
        shop = db.query(cls).filter(Shop.name == shop_data.name).first()
        if shop:
            return shop
        new_shop = Shop(**shop_data.dict())
        db.add(new_shop)
        db.commit()
        db.refresh(new_shop)
        return new_shop


class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    name = Column(String)
    thumbnail = Column(String)
    tags = Column(String)
    shopid = Column(Integer, ForeignKey("shop.id"), index=True)
    price = Column(Float, index=True)


