from fastapi import FastAPI
from pydantic import BaseModel
#from app.adapters.db.mongo import connect_to_mongo, close_mongo_connection
#from app.api.v1.newspage import news_router, summarize_router
from app.adapters.db.mongo import lifespan
from app.api.v1.newspage import news_router, summarize_router


app = FastAPI(lifespan=lifespan)

# Import and include routers after app creation to avoid circular imports
app.include_router(news_router)
app.include_router(summarize_router)

# app = FastAPI(title="Market News API", version="0.1.0")

# app.get("/healthz")
# async def healthz():
#     return {"ok": True}

# @app.on_event("startup")
# async def startup():
#     await connect_to_mongo(app)

# @app.on_event("shutdown")
# async def shutdown():
#     await close_mongo_connection(app)


# # News Related Endpoints will be accessible at /api/v1/news/___
# app.include_router(news_router, prefix="/api/v1/news", tags=["news"])
# app.include_router(summarize_router, prefix="/api/v1/news", tags=["summaries"])

# # Pydantic model for POST request
# class Item(BaseModel):
#     name: str
#     description: str = None
#     price: float
#     tax: float = None

# @app.get("/")
# def read_root():
#     return {"message": "Hello, World!"}

# @app.get("/items/{item_id}")
# def read_item(item_id: int):
#     return {"item_id": item_id, "message": f"This is item {item_id}"}

# @app.post("/items/")
# def create_item(item: Item):
#     return {"item": item, "message": "Item created successfully"}

# @app.get("/health")
# def health_check():
#     return {"status": "healthy", "service": "backend"}



    
    

