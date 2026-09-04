
from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse

class  ProductNotFoundError(Exception):
    pass


class ProductService:
    def __init__(self, db:Session):
        self.db = db
        self.repository = ProductRepository(self.db)
        
        
    def create_product(self, data: ProductCreate) -> Product:
        product = Product(
            name = data.name,
            price = data.price,
            stock  = data.stock
        )
        
        try: 
            self.repository.create(product)
            self.db.commit()
            self.db.refresh(product)
        except Exception as e:
            self.db.rollback()
            raise
        return product
    
    def get_product_by_id(self, product_id:int) -> Product|None:
         product = self.repository.get_product_by_id(product_id=product_id)
         if not product:
             raise ProductNotFoundError("Product Not Found")
         return product
     
    def get_products(self) -> list[Product]:
        return self.repository.get_products()
    
    def update_product(self, product_id: int, product_data):
        product = self.repository.get_product_by_id(product_id)
        if not product:
            raise ProductNotFoundError("Product not found")
        try:
            product = self.repository.update(product, product_data)
            self.db.commit()
            self.db.refresh(product)
            return product
        except Exception as e:
            self.db.rollback()
            raise
        
        
            