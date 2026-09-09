from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.orders import OrderItemResponse, OrderItemCreate, OrderCreate, OrderResponse
from app.models.user import User
from app.api.dependencies import get_current_user, get_db
from sqlalchemy.orm import Session
from app.services.order_service import OrderService
 
 
 
router = APIRouter(
     prefix="/orders",
     tags=["orders"]
 )


@router.post("/", response_model=OrderResponse)
def create_order(order_data: OrderCreate,
                 current_user:User = Depends(get_current_user),
                 db: Session = Depends(get_db) ):
    try:
        service = OrderService(db)
        return service.create_order(order_data.items, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
