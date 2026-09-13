from fastapi import APIRouter, Depends, HTTPException, status, Header
from app.schemas.orders import OrderCreate, OrderResponse
from app.models.user import User
from app.api.dependencies import get_current_user, get_db
from sqlalchemy.orm import Session
from app.services.order_service import OrderService, InsufficientStock, OrderAccessDenied
from app.services.product_service import ProductNotFoundError

 
 
 
router = APIRouter(
     prefix="/orders",
     tags=["orders"]
 )


@router.post("/", response_model=OrderResponse)
def create_order(order_data: OrderCreate,
                 idempotency_key: str = Header(...),
                 current_user:User = Depends(get_current_user),
                 db: Session = Depends(get_db) ):
    try:
        service = OrderService(db)
        return service.create_order(order_data.items, current_user.id, idempotency_key)
    except InsufficientStock as exc:
        raise HTTPException(
            status_code= status.HTTP_409_CONFLICT,
            detail= str(exc)
        ) from exc
        
    except ProductNotFoundError as exc:
        raise HTTPException(
                status_code= status.HTTP_404_NOT_FOUND,
                detail= str(exc)
            ) from exc
        
    except Exception as e:
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )
        

@router.get("/", response_model=list[OrderResponse])
def get_orders_by_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        service = OrderService(db)
        return service.get_orders_by_user(current_user.id)
    except Exception:
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )
        
@router.get("/{order_id}", response_model=OrderResponse)
def get_product_by_id(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        service = OrderService(db)
        order =  service.get_order_by_id(current_user.id, order_id)
        
    except OrderAccessDenied as exc:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail=str(exc)
        )
    except Exception:
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order Not found"
        )
    return order
        
        
