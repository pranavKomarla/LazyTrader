"""
Adapters package for external services and databases.

This package contains adapters for:
- HTTP clients for various news APIs
- Database connections and operations
- Cache implementations
"""

# HTTP API Clients
from .http.newsapi_client import NewsAPIClient
from .http.alphavantage_client import AlphaVantageClient
from .http.finnhub_client import FinnhubClient

# Database adapters
from .db.mongo import connect_to_mongo, close_mongo_connection, get_db

# Cache adapters (future implementations)
# from .cache.redis import RedisCache

__all__ = [
    # HTTP Clients
    "NewsAPIClient",
    "AlphaVantageClient", 
    "FinnhubClient",
    
    # Database functions
    "connect_to_mongo",
    "close_mongo_connection",
    "get_db",
    
    # Cache (future)
    # "RedisCache",
]

