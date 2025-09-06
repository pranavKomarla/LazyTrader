import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

# MongoDB connection settings
MONGO_URL = os.getenv("MONGODB_URL", "mongodb://admin:password@mongo:27017/stockapp?authSource=admin")
DATABASE_NAME = os.getenv("MONGO_DB", "stockapp")

# Async MongoDB client
async def get_mongo_client() -> AsyncIOMotorClient:
    """Get async MongoDB client"""
    client = AsyncIOMotorClient(MONGO_URL)
    try:
        # Test the connection
        await client.admin.command('ping')
        return client
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise

# Sync MongoDB client (for initialization scripts)
def get_sync_mongo_client() -> MongoClient:
    """Get sync MongoDB client"""
    return MongoClient(MONGO_URL)

# Database instance
async def get_database():
    """Get database instance"""
    client = await get_mongo_client()
    return client[DATABASE_NAME]

# Collections
async def get_news_collection():
    """Get news articles collection"""
    db = await get_database()
    return db.news_articles

async def get_market_data_collection():
    """Get market data collection"""
    db = await get_database()
    return db.market_data

async def get_user_preferences_collection():
    """Get user preferences collection"""
    db = await get_database()
    return db.user_preferences
