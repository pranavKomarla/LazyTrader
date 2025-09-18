from pathlib import Path
import os
from dotenv import load_dotenv

# Resolve project root: settings.py → core → yourapp → PROJECT ROOT
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Load .env from project root (change if you keep .env elsewhere)
load_dotenv(PROJECT_ROOT / ".env")

class Config:
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB:  str = os.getenv("MONGO_DB", "appdb")
    FINNHUB_API_KEY: str = os.getenv("FINNHUB_API_KEY")
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY")
    POLYGON_API_KEY: str = os.getenv("POLYGON_API_KEY")
    ALPHAVANTAGE_API_KEY: str = os.getenv("ALPHAVANTAGE_API_KEY")
    ARTICLES_COLLECTION: str = os.getenv("ARTICLES_COLLECTION", "articles")



config = Config()
