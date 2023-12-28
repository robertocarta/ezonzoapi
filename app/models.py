from sqlalchemy import Column, ForeignKey, Integer, String, Float, Index, text
from app.database import Base, engine


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


class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    name = Column(String)
    thumbnail = Column(String)
    tags = Column(String)
    shopid = Column(Integer, ForeignKey("shop.id"), index=True)
    price = Column(Float, index=True)


Base.metadata.create_all(bind=engine)
