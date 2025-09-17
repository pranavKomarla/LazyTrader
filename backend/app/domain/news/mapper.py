# This file will map the DTOs to the base article model to send to Mongo

from __future__ import annotations
from typing import Union, List
from datetime import datetime, timezone
from app.domain.news.models.finnhub_model import FinnhubAPIArticle
from app.domain.news.models.newsapi_model import NewsAPIArticle
from app.domain.news.models.alphavantage_model import AlphavantageAPINewsResponse
from app.domain.news.models.base_model import Article, ArticleSource, ArticleCategory
from app.domain.news.models.alphavantage_model import FeedItem as AVFeedItem
from app.domain.news.models.finnhub_model import FinnhubAPIArticle


ProviderArticle = Union[NewsAPIArticle, AVFeedItem, FinnhubAPIArticle]

def to_article(obj: ProviderArticle,
               source: ArticleSource,
               category: ArticleCategory = ArticleCategory.GENERAL) -> Article:
    if source == ArticleSource.NEWSAPI and isinstance(obj, NewsAPIArticle):
        return map_newsapi_to_article(obj, category)
    if source == ArticleSource.ALPHAVANTAGE and isinstance(obj, AVFeedItem):
        return map_alphavantage_to_article(obj, category)
    # if source == ArticleSource.FINNHUB and isinstance(obj, FinnhubAPIArticle):
    #     return map_finnhub_to_article(obj, category)
    raise TypeError(f"Unsupported source/object combo: {source} / {type(obj).__name__}")


def map_finnhub_to_article(finnhub_article: FinnhubAPIArticle) -> Article:
    """Convert FinnhubAPIArticle to general Article model"""
    return Article(
        id=f"finnhub_{finnhub_article.id}",
        title=finnhub_article.headline,
        content=finnhub_article.summary,
        summary=finnhub_article.summary,
        url=finnhub_article.url,
        source=ArticleSource.FINNHUB,
        source_id=str(finnhub_article.id),
        source_name=finnhub_article.source or "Finnhub",
        category=ArticleCategory(finnhub_article.category.lower()),
        published_at=finnhub_article.published_at,
        created_at=datetime.now(timezone.utc),
        language="en",
        image_url=finnhub_article.image,
        related=finnhub_article.related,
        tickers=[finnhub_article.related] if finnhub_article.related else None
    )

def map_newsapi_to_article(newsapi_article: NewsAPIArticle, category: ArticleCategory = ArticleCategory.GENERAL) -> Article:
    """Convert NewsAPIArticle to general Article model"""
    return Article(
        id=f"newsapi_{hash(newsapi_article.url)}",  # Generate ID from URL hash
        title=newsapi_article.title,
        content=newsapi_article.content,
        summary=newsapi_article.description,
        url=newsapi_article.url,
        source=ArticleSource.NEWSAPI,
        source_id=str(hash(newsapi_article.url)),
        source_name=newsapi_article.source.name,
        category=category,  # NewsAPI doesn't have categories like Finnhub
        published_at=datetime.strptime(str(newsapi_article.publishedAt), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc),
        created_at=datetime.now(timezone.utc),
        language="en",
        image_url=newsapi_article.urlToImage,
        author=newsapi_article.author
    )

def map_alphavantage_to_article(alphavantage_article: AVFeedItem, category: ArticleCategory = ArticleCategory.GENERAL) -> Article:
    """Convert AlphavantageAPINewsResponse to general Article model"""

    return Article(
        id=f"alphavantage_{hash(alphavantage_article.url)}",  # Generate ID from URL hash
        title=alphavantage_article.title,
        content=None,
        summary=alphavantage_article.summary,
        url=alphavantage_article.url,
        source=ArticleSource.ALPHAVANTAGE,
        source_id=str(hash(alphavantage_article.url)),
        source_name=alphavantage_article.source,
        category=category, 
        published_at=alphavantage_article.time_published,
        created_at=datetime.now(timezone.utc),
        language="en",
        image_url=alphavantage_article.banner_image if alphavantage_article.banner_image else None,
        author=", ".join(alphavantage_article.authors) if alphavantage_article.authors else None 

        # Potentially add tickers, topics, sentiment, etc.
    )
