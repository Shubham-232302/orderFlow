from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserServices, UserNotFoundError
from app.api.dependencies import get_current_user, require_admin
from app.models.user import User
from app.repositories.user_repository import UserRepository
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)



@router.get("/me", response_model=UserResponse)
def get_me(curret_user: User = Depends(get_current_user)):
    return curret_user

@router.get("/", response_model=list[UserResponse])
def get_users(current_user: User = Depends(require_admin),
              db:Session = Depends(get_db)):
    repository = UserRepository(db)
    return repository.get_all()


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
        
@router.get("/{user_id}", response_model= UserResponse)
def get_user(
    user_id: int,
    db:Session = Depends(get_db),
    _ = Depends(require_admin)
    ):
    service = UserServices(db)
    try: 
        return service.get_user(user_id)
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc