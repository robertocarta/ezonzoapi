from sqlalchemy import Column, ForeignKey, Integer, String, Float, Index, text
from sqlalchemy.orm import Session
from app.database import Base
from app.schemas import ShopCreate


class Shop(Base):
    __tablename__ = 'shop'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    address = Column(String)
    url = Column(String)

    __table_args__ = (
        Index('idx_shop_location', text("point(lat, lon)"), postgresql_using="gist"),
        )

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


