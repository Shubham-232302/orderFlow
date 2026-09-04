from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str
    price: int = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    
class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: int
    stock: int
    
    
class ProductUpdate(BaseModel):
    name: str | None = None
    price: int | None = None
    stock: int | None = None