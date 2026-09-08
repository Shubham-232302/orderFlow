
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.models.product import Product
from app.services.product_service import ProductNotFoundError
from sqlalchemy.orm import Session
from app.schemas.orders import OrderItemCreate
from app.models.orders import Order
from app.models.order_items import OrderItem



class OrderService:
    def __init__(self, db:Session) -> None:
        self.db = db
        self.product_repository = ProductRepository(db)
        self.order_repository = OrderRepository(db)
        
    def get_product_by_id(self, product_id:int) -> Product:
        product = self.product_repository.get_product_by_id(product_id)
        if not product:
            raise ProductNotFoundError("product not found")
        return product
    
    
    def create_order(self, list_of_items: list[OrderItemCreate], user_id: int) -> Order:
        try:
            total_amount = 0
            validated_items = []
            for item in list_of_items:
                product = self.get_product_by_id(item.product_id)
                if product.stock < item.quantity:
                    raise ValueError("Insufficient stock")
                
                total_amount+= product.price*item.quantity
                validated_items.append({"product_id":item.product_id, "quantity":item.quantity, "unit_price":product.price })
                self.product_repository.update_stock(product, item.quantity)
            order = Order(user_id=user_id, total_amount=total_amount)
            order = self.order_repository.create_order(order)
            
            for ele in validated_items:
                order_item = OrderItem(
                    product_id = ele.get("product_id"),
                    order_id = order.id,
                    quantity = ele.get("quantity"),
                    unit_price = ele.get("unit_price")
                )
                self.order_repository.create_order_item(order_item)
            self.db.commit()
            return order
        except Exception:
            self.db.rollback()
            raise
            
            
        