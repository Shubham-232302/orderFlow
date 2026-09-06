from pydantic import Field, BaseModel
from app.schemas.orderItem import OrderItemCreate



class OrderCreate(BaseModel):
    items: list[OrderItemCreate]
    
    
