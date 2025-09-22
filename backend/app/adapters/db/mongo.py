# init Mongo, Redis, LLM, splitter; attach to app.state
# TODO: make sure to rename this file to lifespan.py

import os
from typing import List, Optional, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from contextlib import asynccontextmanager
# from app.models import Article, ArticleSummary
from fastapi import FastAPI, Request
from app.core.config import config
from app.adapters.db.repositories.article_repository import ArticleRepository
from redis.asyncio import Redis as AsyncRedis
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    mongo_client = AsyncIOMotorClient(config.MONGO_URI)
    await mongo_client.admin.command("ping")
    db: AsyncIOMotorDatabase = mongo_client[config.MONGO_DB]

    # Redis (async) cache
    redis = AsyncRedis.from_url(config.REDIS_URL, decode_responses=True)

    # LLM client
    llm = ChatOpenAI(api_key=config.OPENAI_API_KEY, model=config.OPENAI_MODEL, temperature=0)

    # Text splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.SUMMARY_MAP_CHUNK_SIZE,
        chunk_overlap=config.SUMMARY_MAP_CHUNK_OVERLAP,
    )

    # Initialize repo(s) and create indexes once
    article_repo = ArticleRepository(db, config.ARTICLES_COLLECTION)
    await article_repo.create_indexes()

    # store in app.state for DI
    app.state.mongo_client = mongo_client
    app.state.db = db
    app.state.redis = redis
    app.state.llm = llm
    app.state.splitter = splitter
    app.state.article_repo = article_repo

    try:
        yield
    finally:
        await redis.close()
        mongo_client.close()

# ---- Dependencies to pull from app.state ----
def get_db(request: Request):
    return request.app.state.db

def get_article_repo(request: Request) -> ArticleRepository:
    return request.app.state.article_repo

def get_redis(request: Request) -> AsyncRedis:
    return request.app.state.redis

def get_llm(request: Request) -> ChatOpenAI:
    return request.app.state.llm

def get_splitter(request: Request) -> RecursiveCharacterTextSplitter:
    return request.app.state.splitter

def get_mongo_client(request: Request) -> AsyncIOMotorClient:
    return request.app.state.mongo_client


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