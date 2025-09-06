from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import List, Optional, Dict


class Article(BaseModel):
    id: str
    url: HttpUrl
    title: str
    source: str
    published_at: datetime
    ingested_at: datetime
    snippet: Optional[str] = None
    tickers: List[str] = []
    sentiment: int = 0 # -1, 0, 1
    topics: List[str] = [] # ["general","ai","ipos","smallcaps","macro"]
    cluster_id: Optional[str] = None
    coverage_score: float = 0.0


class ArticleCard(Article):
    pass


class ArticleSummary(BaseModel):
    article_id: str
    tldr: str
    entities: Dict[str, List[str]] = Field(default_factory=lambda: {"indices":[], "sectors":[], "companies":[]})
    model: str = "stub-llm-0.1"
    created_at: datetime


class PageRecap(BaseModel):
    recap_text: str
    themes: List[Dict[str, str]]
    sources: List[Dict[str, int]] = []
    model: str = "stub-llm-0.1"
    created_at: datetime