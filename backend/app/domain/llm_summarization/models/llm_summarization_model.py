from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import List, Optional, Dict, Any


class ArticleDoc(BaseModel):
    id: str = Field(alias="_id")
    title: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    image_url: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None # your subtopic
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] | Dict[str, Any] = None
    content: str
    language: Optional[str] = None
    summary: Optional[str] = None # if you already store any short summary


    # cached summary fields (our per-article AI summary)
    summary_ai: Optional[str] = None
    summary_hash: Optional[str] = None

    # TODO: this is a replica of the Article model, but we need to add the cached summary fields, so we can either create a new model or extend the Article model

class SingleSummaryResponse(BaseModel): # returned by POST /articles/{article_id}/summary
    id: str
    title: Optional[str]
    url: Optional[str]
    summary: str
    cached: bool


class BatchSummaryResult(BaseModel): # returned by POST /articles/summarize-all
    scanned: int
    summarized: int
    skipped_cached: int
    errors: int
    error_ids: List[str] = []


class CategoryBrief(BaseModel): # structure of the long subtopic brief
    overview: str
    key_themes: List[Dict[str, Any]] # [{"headline": str, "bullets": [str, ...]}]
    implications: List[str]
    notable_data_points: List[str]
    top_sources: List[Dict[str, Any]] # [{"name": str, "count": int}]
    article_count: int
    generated_at: datetime