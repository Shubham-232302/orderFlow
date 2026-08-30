from sqlalchemy.orm import Session
from app.core.security import create_access_token, verify_password
from app.repositories.user_repository import UserRepository




class AuthService:
    def __init__(self, db:Session):
        self.repository = UserRepository(db)
        
    def login(self, email:str, password:str) -> str:
        user = self.repository.get_by_email(email)
        
        if not user:
            raise ValueError("Invalid email or password")
        
        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")
            
        if not user.is_active:
            raise ValueError("User is inactive")
        
        return create_access_token(user.id)