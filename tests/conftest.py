import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.db.session import Base
from app.main import app


TEST_DATABASE_URL = (
    "postgresql+psycopg://orderflow:orderflow@localhost:5432/orderflow_test"
)


engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True
)

@pytest.fixture(scope = "session")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    
    
@pytest.fixture
def db_session(setup_database):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    try:
        yield session
    finally:
        session.close
        transaction.rollback()
        connection.close()
        
@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session
        
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
    
    