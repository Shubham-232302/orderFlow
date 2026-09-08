
from app.models.orders import Order
from app.models.order_items import OrderItem

from sqlalchemy.orm import Session

class OrderRepository:
    
    def __init__(self, db: Session):
        self.db = db
        
    
    def create_order(self, order:Order) -> Order:
        self.db.add(order)
        self.db.flush()
        return order
    
    def create_order_item(self, order_item:OrderItem) -> OrderItem|None:
        self.db.add(order_item)
        self.db.flush()
        return order_item