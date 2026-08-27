
from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.api.routes.users import router as users_router

app = FastAPI(
    title = "Order Flow API",
    version = "0.1.0"
)


app.include_router(
    users_router,
    prefix="/api/v1"
)

@app.get("/health")
def read_items():
    return {"message": "Hello, World!"}
