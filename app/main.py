from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_items():
    return {"message": "Hello, World!"}