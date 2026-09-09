
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.models.product import Product
from app.services.product_service import ProductNotFoundError
from sqlalchemy.orm import Session
from app.schemas.orders import OrderItemCreate
from app.models.orders import Order
from app.models.order_items import OrderItem



class InsufficientStock(Exception):
    pass

class OrderService:
    def __init__(self, db:Session) -> None:
        self.db = db
        self.product_repository = ProductRepository(db)
        self.order_repository = OrderRepository(db)
        
    def get_product_for_update(self, product_id:int) -> Product:
        product = self.product_repository.get_product_for_update(product_id)
        if not product:
            raise ProductNotFoundError("product not found")
        return product
    
    
    def create_order(self, list_of_items: list[OrderItemCreate], user_id: int) -> Order:
        quantity = {}
        
        for itm in list_of_items:
            if itm.product_id in quantity:
                quantity[itm.product_id] += itm.quantity
            else:
                quantity[itm.product_id] = itm.quantity
                
                
        try:
            total_amount = 0
            validated_items = []
            for key, value in sorted(quantity.items()):
                product = self.get_product_for_update(key)
                if product.stock < value:
                    raise InsufficientStock("Insufficient stock")
                
                total_amount+= product.price*value
                validated_items.append({"product_id":key, "quantity":value, "unit_price":product.price })
                self.product_repository.update_stock(product, value)
            order = Order(user_id=user_id, total_amount=total_amount)
            order = self.order_repository.create_order(order)
            
            for ele in validated_items:
                order_item = OrderItem(
                    order_id = order.id,
                    product_id=ele["product_id"],
                    quantity=ele["quantity"],
                    unit_price=ele["unit_price"]
                )
                self.order_repository.create_order_item(order_item)
            self.db.commit()
            return order
        except Exception:
            self.db.rollback()
            raise
            
            
        