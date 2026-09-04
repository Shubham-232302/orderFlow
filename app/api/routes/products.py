from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.product import ProductResponse, ProductUpdate,ProductCreate
from app.services.product_service import ProductService, ProductNotFoundError
from app.api.dependencies import get_current_user, require_admin
from app.models.user import User
from app.repositories.user_repository import UserRepository
router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    data:ProductCreate,
    db: Session = Depends(get_db),
    _:User = Depends(require_admin)
    ):
    service = ProductService(db)
    try:
        return service.create_product(data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc)
        )
        
        
@router.get("/", response_model=list[ProductResponse])
def get_all_products(
    db:Session = Depends(get_db),
    _:User =  Depends(get_current_user)
):
    service = ProductService(db)
    return service.get_products()


        
@router.get("/{product_id}", response_model=ProductResponse)
def get_product_by_id(
    product_id: int,
    db:Session = Depends(get_db),
    _:User =  Depends(get_current_user)
    ):
    service = ProductService(db)
    try: 
        return service.get_product_by_id(product_id)
    except ProductNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc)
            )

@router.patch("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def update_product(
    product_id:int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    _:User = Depends(require_admin),
    
):
    service = ProductService(db)
    try:
        return service.update_product(product_id, product_data)
    except ProductNotFoundError as exc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=str(exc)
                ) from exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        

