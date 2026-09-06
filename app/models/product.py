from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.models.order_items import OrderItem


class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    name: Mapped[str]=mapped_column(
                String(255),
                index=True,
                nullable=False
        )
    
    price: Mapped[int] = mapped_column(
            Integer,
            nullable=False
        )
    
    stock: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default= 0 
    )
    
    order_items: Mapped[list["OrderItem"]]= relationship(
        back_populates="product"
    )
    
    
    
    
    