from app.models.user import User

__all__ = ["User"] # important for alembic because we need SQLAlchemy's metadata to know about our models