from sqlalchemy import String, Integer,Float
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base

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