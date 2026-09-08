from pydantic import Field, BaseModel, ConfigDict

# from app.schemas.orderItem import OrderItemCreate




class OrderItemCreate(BaseModel):
    product_id : int 
    quantity: int = Field(gt=0)

class OrderCreate(BaseModel):
    items: list[OrderItemCreate] = Field(min_length=1)
    
    
class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    unit_price: int
    

class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    total_amount: int
    items: list[OrderItemResponse]    
    
