from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, HttpUrl, Field, field_serializer
from datetime import datetime, timezone
from enum import Enum

class ArticleSource(str, Enum):
    FINNHUB = "finnhub"
    NEWSAPI = "newsapi"
    POLYGON = "polygon"
    BENZINGA = "benzinga"
    ALPHAVANTAGE = "alphavantage"

class ArticleCategory(str, Enum):
    GENERAL = "general"
    AI = "ai"
    IPOS = "ipos"
    SMALLCAPS = "smallcaps"
    MACRO = "macro"
    COMPANY = "company"

class Article(BaseModel):
    """General article model that can be mapped from various news sources"""
    
    # Core article information
    id: str  # Unique identifier (could be source_id + source)
    title: str
    content: Optional[str] = None
    summary: Optional[str] = None
    url: HttpUrl
    
    # Source information
    source: ArticleSource
    source_id: str  # Original ID from the source API
    source_name: str  # Human-readable source name (e.g., "BBC News", "Reuters")
    
    # Metadata
    category: ArticleCategory = ArticleCategory.GENERAL
    published_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    # Content metadata
    language: str = "en"
    image_url: Optional[HttpUrl] = None
    author: Optional[str] = None
    
    # Financial/Stock specific
    tickers: Optional[List[str]] = None  # Stock symbols mentioned
    sentiment: Optional[float] = None  # -1.0 to 1.0 sentiment score
    topics: Optional[List[str]] = None  # Tags/topics
    
    # Processing metadata
    is_processed: bool = False
    is_summarized: bool = False
    coverage_score: Optional[float] = None
    
    model_config = {
        "use_enum_values": True,  # serialize enums as their values
    }

    # Pydantic v2: use field_serializer instead of json_encoders
    @field_serializer("published_at", "created_at", "updated_at", when_used="json")
    def _ser_dt(self, v: Optional[datetime], _info):
        return v.isoformat() if v else None