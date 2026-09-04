from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate,ProductResponse,ProductUpdate




class ProductRepository:
    
    
    def __init__(self, db:Session) -> None:
        self.db = db
        
    def get_products(self) -> list[Product]:
        return self.db.query(Product).all()
    
    def get_product_by_id(self, product_id: int) -> Product|None:
        statement = select(Product).where(Product.id == product_id)
        return self.db.scalar(statement)
    
    def create(self, product:Product) -> Product|None:
        self.db.add(product)
        self.db.flush()
        return product