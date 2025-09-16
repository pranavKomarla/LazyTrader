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
    if source == ArticleSource.FINNHUB and isinstance(obj, FinnhubAPIArticle):
        return map_finnhub_to_article(obj, category)
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

def map_newsapi_to_article(newsapi_article: NewsAPIArticle) -> Article:
    """Convert NewsAPIArticle to general Article model"""
    return Article(
        id=f"newsapi_{hash(newsapi_article.url)}",  # Generate ID from URL hash
        title=newsapi_article.title,
        content=newsapi_article.content,
        summary=newsapi_article.description,
        url=newsapi_article.url,
        source=ArticleSource.NEWSAPI,
        source_id=str(hash(newsapi_article.url)),
        source_name=newsapi_article.source.get("name", "Unknown") if newsapi_article.source else "Unknown",
        category=ArticleCategory.GENERAL,  # NewsAPI doesn't have categories like Finnhub
        published_at=newsapi_article.published_at,
        created_at=datetime.now(timezone.utc),
        language="en",
        image_url=newsapi_article.url_to_image,
        author=newsapi_article.author
    )

def map_alphavantage_to_article(alphavantage_article: AVFeedItem, category: ArticleCategory = ArticleCategory.GENERAL) -> Article:
    """Convert AlphavantageAPINewsResponse to general Article model"""

    return Article(
        id=f"alphavantage_{hash(alphavantage_article.url)}",  # Generate ID from URL hash
        title=alphavantage_article.title,
        content=None,
        summary=alphavantage_article.description,
        url=alphavantage_article.url,
        source=str(ArticleSource.ALPHAVANTAGE),
        source_id=str(hash(alphavantage_article.url)),
        source_name=alphavantage_article.source.get("name", "Unknown") if alphavantage_article.source else "Unknown",
        category=category, 
        published_at=alphavantage_article.time_published,
        created_at=datetime.now(timezone.utc),
        language="en",
        image_url=alphavantage_article.banner_image,
        author=alphavantage_article.authors # potiently change to a string of authors
    )

def map_articles_to_article(articles: List[Union[FinnhubAPIArticle, NewsAPIArticle, AlphavantageAPINewsResponse]]) -> List[Article]:
    """Convert a list of mixed article types to general Article models"""
    result = []
    for article in articles:
        if isinstance(article, FinnhubAPIArticle):
            result.append(map_finnhub_to_article(article))
        elif isinstance(article, NewsAPIArticle):
            result.append(map_newsapi_to_article(article))
        elif isinstance(article, AlphavantageAPINewsResponse):
            result.append(map_alphavantage_to_article(article))
    return result