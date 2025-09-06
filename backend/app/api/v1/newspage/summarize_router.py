from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List
from app.services import cache, db, summarize_llm


router = APIRouter()


class SummarizeArticleBody(BaseModel):
    id: str


@router.post("/summarize-article")
async def summarize_article_endpoint(body: SummarizeArticleBody):
    key = f"article_summary:{body.id}"
    cached = await cache.get(key)
    if cached:
        return cached


    article = await db.get_article(body.id)
    if not article:
        raise HTTPException(status_code=404, detail={"code":"NOT_FOUND","message":"article not found"})


    summary = await summarize_llm.summarize_article(article)
    await db.save_article_summary(summary)
    payload = summary.dict()
    await cache.set(key, payload, ttl=259200) # 3 days
    return payload


class SummarizePageBody(BaseModel):
    article_ids: List[str]


@router.post("/summarize-page")
async def summarize_page_endpoint(body: SummarizePageBody):
    if not body.article_ids:
        raise HTTPException(status_code=400, detail={"code":"INVALID_PARAM","message":"article_ids required"})


    # Deterministic key (shortened)
    joined = ",".join(sorted(body.article_ids))
    key = "page_recap:" + str(abs(hash(joined)))


    cached = await cache.get(key)
    if cached:
        return cached


    articles = [a for a in (await db.get_articles(body.article_ids)) if a]
    recap = await summarize_llm.summarize_page(articles)
    payload = recap.dict()
    await cache.set(key, payload, ttl=43200) # 12h
    return payload