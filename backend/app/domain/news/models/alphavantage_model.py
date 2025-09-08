from typing import List, Optional
from pydantic import BaseModel


class Author(BaseModel):
    __root__: str  # since it's just a list of strings


class Topic(BaseModel):
    topic: str
    relevance_score: float


class TickerSentiment(BaseModel):
    ticker: str
    relevance_score: float
    ticker_sentiment_score: float
    ticker_sentiment_label: str


class FeedItem(BaseModel):
    title: str
    url: str
    time_published: str
    authors: List[str]
    summary: str
    banner_image: Optional[str]
    source: str
    category_within_source: Optional[str]
    source_domain: str
    topics: List[Topic]
    overall_sentiment_score: float
    overall_sentiment_label: str
    ticker_sentiment: List[TickerSentiment]


class AlphavantageAPINewsResponse(BaseModel):
    items: str
    sentiment_score_definition: str
    relevance_score_definition: str
    feed: List[FeedItem]
