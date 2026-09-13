
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.models.product import Product
from app.services.product_service import ProductNotFoundError
from sqlalchemy.orm import Session
from app.schemas.orders import OrderItemCreate
from app.models.orders import Order
from app.models.order_items import OrderItem
from sqlalchemy.exc import IntegrityError
from psycopg.errors import UniqueViolation


class InsufficientStock(Exception):
    pass

class OrderAccessDenied(Exception):
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
    
    
    def create_order(self, list_of_items: list[OrderItemCreate], user_id: int, idempotency_key: str) -> Order:
        quantity = {}
        
        order = self.order_repository.get_by_idempotency_key(user_id, idempotency_key)
        if order:
            return order
        
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
            order = Order(user_id=user_id, total_amount=total_amount, idempotency_key=idempotency_key)
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
        except IntegrityError as exc:
            self.db.rollback()
            print(f"IntegrityError: {exc.orig}")
            if isinstance(exc.orig, UniqueViolation):
                constraint_name = exc.orig.diag.constraint_name

                if constraint_name == "uq_orders_user_id_idempotency_key":
                    existing_order = self.order_repository.get_by_idempotency_key(
                        user_id=user_id,
                        idempotency_key=idempotency_key,
                    )

                    if existing_order:
                        return existing_order

            raise
        except Exception:
            self.db.rollback()
            raise
            
    
    def get_orders_by_user(self, user_id:int) -> list[Order]:
        return self.order_repository.get_orders_by_user(user_id)
    
    def get_order_by_id(self, user_id: int, order_id: int) -> Order | None:
        
        order = self.order_repository.get_order_by_id(order_id)
        if order  and order.user_id != user_id:
            raise OrderAccessDenied("Access Denied")
        return order
                    
        