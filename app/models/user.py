from datetime import datetime
from sqlalchemy import Boolean, DateTime, String, func, Enum as sqlenum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from enum import Enum



class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    
    name: Mapped[str|None] = mapped_column(
        String(100),
        nullable=True,
    )
    
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    role: Mapped[UserRole] = mapped_column(
        sqlenum(UserRole, values_callable = lambda enum_cls: [member.value for member in enum_cls]),
        default= UserRole.USER,
        nullable=False
    )
    
    
