import os
from typing import List, Optional, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from contextlib import asynccontextmanager
# from app.models import Article, ArticleSummary
from fastapi import FastAPI, Request
from app.core.config import config
from app.adapters.db.repositories.article_repository import ArticleRepository

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    mongo_client = AsyncIOMotorClient(config.MONGO_URI)
    await mongo_client.admin.command("ping")
    db: AsyncIOMotorDatabase = mongo_client[config.MONGO_DB]

    # Initialize repo(s) and create indexes once
    article_repo = ArticleRepository(db, config.ARTICLES_COLLECTION)
    await article_repo.create_indexes()

    # store in app.state for DI
    app.state.mongo_client = mongo_client
    app.state.db = db
    app.state.article_repo = article_repo

    yield  # ===== app runs =====

    # --- Shutdown ---
    mongo_client.close()

# ---- Dependencies to pull from app.state ----
def get_db(request: Request):
    return request.app.state.db

def get_article_repo(request: Request) -> ArticleRepository:
    return request.app.state.article_repo


# _articles: dict[str, Article] = {}
# _summaries: dict[str, ArticleSummary] = {}


# async def seed(articles: List[Article]):
#     for a in articles:
#         _articles[a.id] = a


# async def get_article(article_id: str) -> Optional[Article]:
#     return _articles.get(article_id)


# async def get_articles(ids: List[str]) -> List[Optional[Article]]:
#     return [await get_article(i) for i in ids]


# async def save_article_summary(summary: ArticleSummary):
#     _summaries[summary.article_id] = summary


# async def query_articles(tab: str, cutoff: datetime, sentiment: str, sources: str, limit: int, watchlist: List[str], cursor: Optional[str]):
# # Very naive filter; replace with indexed queries in real DB
#     res = []
#     for a in _articles.values():
#         if tab not in a.topics:
#             continue

#         if a.published_at < cutoff:
#             continue

#         if sentiment != "any":
#             if sentiment == "bull" and a.sentiment <= 0: continue
#             if sentiment == "bear" and a.sentiment >= 0: continue
#             if sentiment == "neutral" and a.sentiment != 0: continue
#         if sources != "all":
#             allowed = {s.strip().lower() for s in sources.split(",")}
#         if a.source.lower() not in allowed:
#             continue
#         if watchlist:
#             if not any(t in (a.tickers or []) for t in watchlist):
#                 continue

#         res.append(a)
#         # No real cursor yet
#     res.sort(key=lambda x: (x.published_at, x.coverage_score), reverse=True)
#     return res[:limit]