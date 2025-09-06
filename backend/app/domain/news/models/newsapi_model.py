from typing import List, Optional
from pydantic import BaseModel


class NewsAPISource(BaseModel):
    id: Optional[str]
    name: str


class NewsAPIArticle(BaseModel):
    source: NewsAPISource
    author: Optional[str]
    title: str
    description: Optional[str]
    url: str
    urlToImage: Optional[str]
    publishedAt: str
    content: Optional[str]


class NewsAPIResponse(BaseModel):
    status: str
    totalResults: int
    articles: List[NewsAPIArticle]
