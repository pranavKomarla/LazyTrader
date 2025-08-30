from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

app.get("/healthz")
async def healthz():
    return {"ok": True}

# Pydantic model for POST request
class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id, "message": f"This is item {item_id}"}

@app.post("/items/")
def create_item(item: Item):
    return {"item": item, "message": "Item created successfully"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "backend"}

