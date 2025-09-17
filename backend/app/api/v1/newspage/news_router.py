from __future__ import annotations
from typing import List, Optional

from fastapi import APIRouter, Depends
from datetime import datetime
from typing_extensions import Annotated

from app.domain.news.models.base_model import Article
from app.adapters.db.repositories.article_repository import ArticleRepository
from app.main import get_article_repo

router = APIRouter(prefix="/articles", tags=["articles"])

RepoDep = Annotated[ArticleRepository, Depends(get_article_repo)]

@router.post("/upsert", response_model=Article)
async def upsert_article(article: Article, repo: RepoDep):
    return await repo.upsert_one(article)

@router.post("/bulk-upsert")
async def bulk_upsert(articles: List[Article], repo: RepoDep):
    return await repo.upsert_many(articles)

@router.get("/{article_id}", response_model=Optional[Article])
async def get_article(article_id: str, repo: RepoDep):
    return await repo.get_by_id(article_id)

@router.delete("/{article_id}")
async def delete_article(article_id: str, repo: RepoDep):
    deleted = await repo.delete_by_id(article_id)
    return {"deleted": deleted}

@router.get("/", response_model=List[Article])
async def list_articles(
    category: str | None = None,
    source: str | None = None,
    ticker: str | None = None,
    since: datetime | None = None,
    limit: int = 50,
    skip: int = 0,
    repo: RepoDep = Depends(),
):
    return await repo.list(
        category=category, source=source, ticker=ticker, since=since, limit=limit, skip=skip
    )
