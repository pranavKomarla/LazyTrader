from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone


class Author(BaseModel):
    root_symbol: str  # since it's just a list of strings


class Topic(BaseModel):
    topic: str
    relevance_score: float


class TickerSentiment(BaseModel):
    ticker: str
    relevance_score: float
    ticker_sentiment_score: float
    ticker_sentiment_label: str # in the future - we can add a list of labels such as Literal["Bullish", "Somewhat-Bullish", "Neutral", "Somewhat-Bearish", "Bearish"]


class FeedItem(BaseModel):
    title: str
    url: str
    time_published: datetime
    authors: List[str]
    summary: str
    banner_image: Optional[str]
    source: str
    category_within_source: Optional[str]
    source_domain: str
    topics: List[Topic] = Field(default_factory=list)
    overall_sentiment_score: Optional[float] = None
    overall_sentiment_label: Optional[
        Literal["Bullish", "Somewhat-Bullish", "Neutral", "Somewhat-Bearish", "Bearish"]
    ] = None

    ticker_sentiment: List[TickerSentiment] = Field(default_factory=list)

    @field_validator("time_published", mode="before")
    @classmethod
    def parse_time(cls, v):
        if isinstance(v, datetime):
            return v
        return datetime.strptime(v, "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)


class AlphavantageAPINewsResponse(BaseModel):
    items: str
    sentiment_score_definition: str
    relevance_score_definition: str
    feed: List[FeedItem] = Field(default_factory=list)
