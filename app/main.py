
from fastapi import FastAPI

app = FastAPI(
    title = "Order Flow API",
    version = "0.1.0"
)

@app.get("/health")
def read_items():
    return {"message": "Hello, World!"}