"""
News domain models package.

This package contains all the data models for the news domain, including:
- Base models and enums
- API-specific DTOs for different news sources
- Summary and recap models
"""

# Base models and enums
from .base_model import Article, ArticleSource, ArticleCategory

# API-specific models
from .finnhub_model import FinnhubAPIArticle
from .newsapi_model import NewsAPIArticle, NewsAPISource, NewsAPIResponse
from .alphavantage_model import (
    Author, 
    Topic, 
    TickerSentiment, 
    FeedItem, 
    AlphavantageAPINewsResponse
)

# Summary models
from .summary import ArticleSummary, PageRecap

__all__ = [
    # Base models
    "Article",
    "ArticleSource", 
    "ArticleCategory",
    
    # Finnhub models
    "FinnhubAPIArticle",
    
    # NewsAPI models
    "NewsAPIArticle",
    "NewsAPISource", 
    "NewsAPIResponse",
    
    # Alpha Vantage models
    "Author",
    "Topic",
    "TickerSentiment", 
    "FeedItem",
    "AlphavantageAPINewsResponse",
    
    # Summary models
    "ArticleSummary",
    "PageRecap",
]
