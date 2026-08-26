from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase , sessionmaker


DATABASE_URL = "postgresql+psycopg://orderflow:orderflow@localhost:5432/orderflow_dev"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# pool_pre_ping=True -> if postgre sql closes an idle connection, sqlalchemy can detect the stale connection 
# and obtain a valid one instead of giving application a database error
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit= False
    )

class Base(DeclarativeBase):
    pass