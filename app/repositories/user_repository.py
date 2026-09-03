from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserUpdate

class UserRepository:
    def __init__(self, db:Session) -> None:
        self.db = db
        
    def get_by_email(self, email:str) -> User | None:
        statement = select(User).where(User.email == email)
        return self.db.scalar(statement)
    
    def get_by_id(self, id:int) -> User | None:
        statement = select(User).where(User.id == id)
        return self.db.scalar(statement)
    
    def create(self, user:User) -> User:
        self.db.add(user)
        self.db.flush()
        
        return user
    
    def get_all(self) -> list[User]:
        statement = self.db.query(User).all()
        return statement
    
    def update_user(self, user:User, update_user: UserUpdate):
        
        update_data = update_user.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(user, field, value)

        self.db.flush()
        