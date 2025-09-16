# This service will call providers -> validate the DTOs -> upsert via repo
from typing import List
from app.domain.news.models import Article
from app.domain.news.models.alphavantage_model import AlphavantageAPINewsResponse
from app.domain.news.models.finnhub_model import FinnhubAPIArticle
from app.domain.news.models.newsapi_model import NewsAPIArticle
from app.domain.news.models.base_model import ArticleSource, ArticleCategory
#from app.adapters.http.newsapi_client import NewsAPIClient
from app.adapters.http.alphavantage_client import AlphaVantageClient
from app.adapters.http.finnhub_client import FinnhubClient
from app.domain.news.mapper import to_article
#from app.services.db import upsert_article


# First we need to call the providers

async def ingest_articles():

    #newsapi = NewsAPIClient()
    alphavantage = AlphaVantageClient()
    #finnhub = FinnhubClient()

    #newsapi_items = await newsapi.get_everything()                # -> List[NewsAPIArticle]
    av_resp = await alphavantage.get_news_sentiment()             # -> AlphavantageAPINewsResponse
    av_items = av_resp.feed                                       # -> List[AVFeedItem]
    # finnhub_items = await finnhub.get_news()                    # -> List[FinnhubAPIArticle]

    #articles = [*newsapi_articles, *alphavantage_articles] #, *finnhub_articles]

    articles: List[Article] = [
        #*[to_article(x, ArticleSource.NEWSAPI, ArticleCategory.GENERAL) for x in newsapi_items],
        *[to_article(x, ArticleSource.ALPHAVANTAGE, ArticleCategory.GENERAL) for x in av_items],
        # *[to_article(x, ArticleSource.FINNHUB, ArticleCategory.GENERAL) for x in finnhub_items],
    ]
    return articles



    



