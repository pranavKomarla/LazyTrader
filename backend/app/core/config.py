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

    # OpenAI / LLM
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    PROMPT_VERSION: str = os.getenv("PROMPT_VERSION", "v1")

    # Summarization tuning
    SUMMARY_MAP_CHUNK_SIZE: int = 1000      # Max 1000 characters per chunk
    SUMMARY_MAP_CHUNK_OVERLAP: int = 200    # 200 character overlap between chunks
    MAX_MAP_CONCURRENCY: int = 8
    SUMMARY_BULLET_TARGET: int = 4 # bullets per chunk in per-article map

    # Redis + Celery
    REDIS_URL: str = os.getenv("REDIS_URL")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND")

    '''
    # Instead of:
    # "Token limit exceeded" 

    # You get:
    # Chunk 1: Summary of first 1000 chars 
    # Chunk 2: Summary of next 1000 chars 
    # Chunk 3: Summary of next 1000 chars 
    # Final: Combined summary of entire article 
    '''


    # Category brief limits
    CATEGORY_MAX_ARTICLES: int = 300 # upper bound to control cost



config = Config()
