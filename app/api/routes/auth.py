from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import AuthService




router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/login", response_model=TokenResponse)
def login(data:LoginRequest, db:Session = Depends(get_db)):
    service = AuthService(db)
    try:
        access_token = service.login(
            data.email, data.password
        )
    except ValueError as exc:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= str(exc)
        ) from exc
    
    return {
        "access_token":access_token,
        "token_type": "bearer"
    }