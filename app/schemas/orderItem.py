from pydantic import BaseModel, ConfigDict, Field





class OrderItemCreate(BaseModel):
    product_id : int 
    quantity: int = Field(gt=0)
    
