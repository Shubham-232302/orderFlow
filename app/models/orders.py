from sqlalchemy import Integer, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.order_items import OrderItem



class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "idempotency_key",
            name="uq_orders_user_id_idempotency_key"
        ),
    )
    
    id: Mapped[int] = mapped_column(
        primary_key=True
    )
    
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )
    
    total_amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    
    idempotency_key: Mapped[str] = mapped_column(
        String(36),
        nullable= False
    )
    
    user: Mapped["User"] = relationship(
        back_populates= "orders"
    )
    
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan"
    )