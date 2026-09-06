from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.orders import Order

class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(
        primary_key=True
    )
    
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False
    )
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"),
        nullable=False
    )
    
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    
    unit_price: Mapped[int] = mapped_column(
        Integer,
        nullable= False
    )
    
    product: Mapped["Product"] = relationship(
        back_populates="order_items"
    )
    
    order: Mapped["Order"] = relationship(
        back_populates="items"
    )
    
    