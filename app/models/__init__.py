from app.models.user import User
from app.models.product import Product

__all__ = ["User", "Product"] # important for alembic because we need SQLAlchemy's metadata to know about our models