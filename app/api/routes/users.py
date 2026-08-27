from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserServices


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)



@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data:UserCreate,
    db: Session = Depends(get_db)
):
    service = UserServices(db)
    try:
        return service.create_user(data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc)
        )