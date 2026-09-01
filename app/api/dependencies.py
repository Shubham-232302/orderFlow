from  fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
import jwt
from app.core.config import settings
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.repositories.user_repository import UserRepository
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("User id missing")
        
        user_id = int(user_id)
        
        user_repository = UserRepository(db)
        
        user = user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        if not user.is_active:
            raise ValueError("User is not active")
        
        return user
    
    except (jwt.InvalidTokenError,ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication error",
            headers={"WWW-Authenticate":"Bearer"}
        )



def require_admin(current_user: User = Depends(get_current_user)) -> User:
    
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Forbidden"
        )
    return current_user
        
    