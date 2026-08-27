from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate



class UserServices:
    def __init__(self, db:Session) -> None:
        self.repository = UserRepository(db)
        self.db = db
        
    def create_user(self, data:UserCreate)-> User:
        existing_user = self.repository.get_by_email(data.email)
        if existing_user:
            raise ValueError("User with this email id already exists")
        
        user = User(
            email = data.email,
            name = data.name
        )
        try:
            self.repository.create(user)
            self.db.commit()
            self.db.refresh(user)
        except IntegrityError:
            self.db.rollback()
            raise ValueError("User with this email is already exists")
        except Exception:
            self.db.rollback()
            raise
        return user
    
    def get_user(self, id:int) -> User:
        user = self.repository.get_by_id(id)
        if not user:
            raise ValueError("User Not Found")
        return user