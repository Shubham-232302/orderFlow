import hashlib
import secrets

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
            name = data.name,
            password_hash = self._hash_password(data.password)
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

    @staticmethod
    def _hash_password(password: str) -> str:
        salt = secrets.token_bytes(16)
        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            600_000,
        )
        return f"{salt.hex()}:{password_hash.hex()}"