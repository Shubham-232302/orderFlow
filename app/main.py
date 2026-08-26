
from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.dependencies import get_db

app = FastAPI(
    title = "Order Flow API",
    version = "0.1.0"
)

@app.get("/health")
def read_items():
    return {"message": "Hello, World!"}



@app.get("/health/db")
def database_health(db:Session = Depends(get_db)):
    result = db.execute(text("SELECT 1"))
    return {"database":result.scalar()}