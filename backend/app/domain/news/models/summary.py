from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import List, Optional, Dict

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