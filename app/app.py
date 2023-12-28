from fastapi import FastAPI, Depends
from mangum import Mangum
import uvicorn

from app.database import SessionLocal, engine
from app.schemas import ProductCreate, ProductBase
from app.models import Base, Shop, Product, Session

app = FastAPI()
handler = Mangum(app)

Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/products/", response_model=ProductBase)
def create_product(product_data: ProductCreate, db: Session = Depends(get_db)):
    db = SessionLocal()
    shop = Shop.get_or_create(db, product_data.shop)
    del product_data.shop
    new_product = Product(**product_data.dict(), shopid=shop.id)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)  # type: ignore
