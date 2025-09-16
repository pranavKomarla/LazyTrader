import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

from app.core.config import config

MONGO_URI = config.MONGO_URI
MONGO_DB = config.MONGO_DB
FINNHUB_API_KEY = config.FINNHUB_API_KEY
ALPHAVANTAGE_API_KEY = config.ALPHAVANTAGE_API_KEY

# Async MongoDB client
async def get_mongo_client() -> AsyncIOMotorClient:
    """Get async MongoDB client"""
    client = AsyncIOMotorClient(MONGO_URI)
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
    return MongoClient(MONGO_URI)

# Database instance
async def get_database():
    """Get database instance"""
    client = await get_mongo_client()
    return client[MONGO_DB]

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
