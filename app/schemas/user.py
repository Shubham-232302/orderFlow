from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models.user import UserRole

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: UserRole = Field(default=UserRole.USER)
    
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: EmailStr
    name: str
    is_active: bool
    role: str
    created_at: datetime
    
    
class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    role: UserRole | None = None
