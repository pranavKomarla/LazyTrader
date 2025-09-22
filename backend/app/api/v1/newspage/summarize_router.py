from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from datetime import datetime
from typing import List
from app.utils.helpers import compute_article_hash
from app.domain.llm_summarization.services.llm_routines import summarize_article_text
from app.adapters.cache.keys import MODEL, PVER
from app.domain.llm_summarization.models.llm_summarization_model import ArticleDoc, SingleSummaryResponse
from app.core.config import config
from app.adapters.cache.keys import k_art_sum, k_art_hash
from app.adapters.db.mongo import get_db
from app.adapters.cache.json import cache_get_json, cache_set_json
from app.utils.helpers import compute_article_hash
from app.domain.llm_summarization.models.llm_summarization_model import ArticleDoc
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis as AsyncRedis
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.domain.llm_summarization.models.llm_summarization_model import BatchSummaryResult
from fastapi.responses import JSONResponse
import hashlib
import json
from app.adapters.db.mongo import get_redis, get_llm, get_splitter


router = APIRouter()


@router.post("/articles/{article_id}/summary", response_model=SingleSummaryResponse)
async def summarize_single_article(article_id: str, force: bool = Query(False, description="Ignore cache and recompute"), db: AsyncIOMotorDatabase = Depends(get_db)):
    redis: AsyncRedis = Depends(get_redis)
    llm: ChatOpenAI = Depends(get_llm)
    splitter: RecursiveCharacterTextSplitter = Depends(get_splitter)


    raw = await db.articles.find_one({"_id": article_id})
    if not raw:
        raise HTTPException(status_code=404, detail="Article not found")
    art = ArticleDoc.model_validate(raw)
    if not art.content or not art.content.strip():
        raise HTTPException(status_code=400, detail="Article has no content to summarize")


    h = await compute_article_hash(art)


    if not force:
        memo = await cache_get_json(redis, k_art_sum(art.id))
        if memo and memo.get("summary_hash") == h:
            return SingleSummaryResponse(id=art.id, title=art.title, url=art.url, summary=memo["summary"], cached=True)


    # Compute fresh
    summary = await summarize_article_text(llm, splitter, title=art.title or "", url=art.url, content=art.content, n_map_bullets=config.SUMMARY_BULLET_TARGET)


    # Persist
    await db.articles.update_one({"_id": art.id}, {"$set": {"summary_ai": summary, "summary_hash": h}})
    await cache_set_json(redis, k_art_sum(art.id), {"summary": summary, "summary_hash": h, "article_id": art.id, "model": MODEL, "pver": PVER, "created_at": datetime.now(timezone.utc).isoformat()})
    await redis.set(k_art_hash(art.id), h)


    return SingleSummaryResponse(id=art.id, title=art.title, url=art.url, summary=summary, cached=False)


@router.post("/articles/summarize-all", response_model=BatchSummaryResult)
async def summarize_all_endpoint(
    since: Optional[datetime] = Query(None, description="Only summarize articles since this UTC timestamp"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: Optional[int] = Query(None, ge=1, le=10000),
    force: bool = Query(False, description="Ignore cache and recompute"),
    concurrency: Optional[int] = Query(None, ge=1, le=64),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    redis: AsyncRedis = Depends(get_redis)
    llm: ChatOpenAI = Depends(get_llm)
    splitter: RecursiveCharacterTextSplitter = Depends(get_splitter)


    q: Dict[str, Any] = {}
    if since:
        q["published_at"] = {"$gte": since}
    if category:
        q["category"] = category


    projection = {"_id": 1, "title": 1, "url": 1, "content": 1, "summary_ai": 1, "summary_hash": 1}
    cursor = db.articles.find(q, projection=projection).sort("published_at", -1)
    if limit:
        cursor = cursor.limit(limit)


    sem = asyncio.Semaphore(concurrency or config.MAX_MAP_CONCURRENCY)


    scanned = summarized = skipped_cached = errors = 0
    error_ids: List[str] = []


    async for raw in cursor:
        scanned += 1
        try:
            art = ArticleDoc.model_validate(raw)
            if not art.content or not art.content.strip():
                skipped_cached += 1
                continue
            h = await compute_article_hash(art)
            if not force:
                memo = await cache_get_json(redis, k_art_sum(art.id))
                if memo and memo.get("summary_hash") == h:
                    skipped_cached += 1
                continue


            async with sem:
                summary = await summarize_article_text(llm, splitter, title=art.title or "", url=art.url, content=art.content, n_map_bullets=config.SUMMARY_BULLET_TARGET)


            await db.articles.update_one({"_id": art.id}, {"$set": {"summary_ai": summary, "summary_hash": h}})
            await cache_set_json(redis, k_art_sum(art.id), {"summary": summary, "summary_hash": h, "article_id": art.id, "model": MODEL, "pver": PVER, "created_at": datetime.now(timezone.utc).isoformat()})
            await redis.set(k_art_hash(art.id), h)
            summarized += 1
        except Exception:
            errors += 1
            try:
                error_ids.append(str(raw.get("_id")))
            except Exception:
                pass


    return BatchSummaryResult(scanned=scanned, summarized=summarized, skipped_cached=skipped_cached, errors=errors, error_ids=error_ids[:50])


@router.get("/summaries/category")
async def get_category_brief(
    category: str = Query(..., description="Category name (subtopic)"),
    since: datetime = Query(..., description="Start (UTC)"),
    until: Optional[datetime] = Query(None, description="End (UTC), defaults to now"),
    mode: str = Query("fast", pattern="^(fast|strict)$", description="fast=serve cache if present; strict=recompute if agg changed"),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    redis: AsyncRedis = Depends(get_redis)
    llm: ChatOpenAI = Depends(get_llm)
    splitter: RecursiveCharacterTextSplitter = Depends(get_splitter)


    until = until or datetime.now(timezone.utc)
    if since.tzinfo is None:
        since = since.replace(tzinfo=timezone.utc)
    if until.tzinfo is None:
        until = until.replace(tzinfo=timezone.utc)


    since_iso = since.astimezone(timezone.utc).isoformat()
    until_iso = until.astimezone(timezone.utc).isoformat()

    # Build aggregate over ids + hashes
    q: Dict[str, Any] = {"category": category, "published_at": {"$gte": since, "$lte": until}}
    cursor = db.articles.find(q, projection={"_id": 1, "summary_hash": 1, "content": 1, "source": 1, "title": 1}).sort("published_at", -1).limit(config.CATEGORY_MAX_ARTICLES)

    ids: List[str] = []
    pairs: List[Tuple[str, str]] = []
    bullets: List[str] = []

    async for d in cursor:
        _id = str(d.get("_id"))
        ids.append(_id)
        h = d.get("summary_hash") or stable_hash(d.get("content") or "")
        pairs.append((_id, h))
        # TL;DR bullets from cache or compute quick
        b = await redis.get(k_art_tldr(_id))
        if not b:
            content = d.get("content") or ""
        if content:
            b = await quick_tldr_bullets(llm, splitter, content=content, n_bullets=3)
        await redis.set(k_art_tldr(_id), b, ex=7 * 24 * 3600)
        if b:
            bullets.append(b)
        
    if not ids:
        raise HTTPException(status_code=404, detail="No matching articles for category/time window")

    pairs.sort(key=lambda x: x[0])
    agg_str = "|".join(f"{i}:{h}" for i, h in pairs)
    agg_hash = hashlib.sha256(agg_str.encode("utf-8")).hexdigest()


    # Cache keys
    brief_key = k_cat_brief(category, since_iso, until_iso)
    agg_key = k_cat_agg(category, since_iso, until_iso)


    # FAST mode: return cached even if stale, and refresh in background
    cached = await cache_get_json(redis, brief_key)
    cached_agg = await redis.get(agg_key)

    if mode == "fast":
        if cached and cached_agg == agg_hash:
            return JSONResponse(cached)
        # Stale-while-revalidate: return cached if any, kick bg job
        if cached:
            # enqueue background rebuild
            build_category_brief_task.delay(category, since_iso, until_iso)
            return JSONResponse(cached)
        # nothing cached → build now
        brief = await reduce_category_long_brief(llm, category=category, since_iso=since_iso, until_iso=until_iso, bullets_lines=bullets)
        brief.article_count = len(ids)
        payload = json.loads(brief.model_dump_json())
        await cache_set_json(redis, brief_key, payload)
        await redis.set(agg_key, agg_hash)
        return JSONResponse(payload)
    
    # STRICT mode: recompute if agg changed; otherwise return cached
    if cached and cached_agg == agg_hash:
        return JSONResponse(cached)

    # Recompute
    brief = await reduce_category_long_brief(llm, category=category, since_iso=since_iso, until_iso=until_iso, bullets_lines=bullets)
    brief.article_count = len(ids)
    payload = json.loads(brief.model_dump_json())
    await cache_set_json(redis, brief_key, payload)
    await redis.set(agg_key, agg_hash)
    return JSONResponse(payload)

# Optional: multi-category in one request
class CategoriesRequest(BaseModel):
    categories: List[str]
    since: datetime
    until: Optional[datetime] = None
    mode: str = "fast" # fast | strict


@router.post("/summaries/categories")
async def get_multi_category_briefs(body: CategoriesRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    results: Dict[str, Any] = {}
    for cat in body.categories:
        # call the internal logic by issuing a sub-request (simple call to handler)
        resp = await get_category_brief(category=cat, since=body.since, until=body.until, mode=body.mode, db=db)
        # FastAPI Response → content
        results[cat] = json.loads(resp.body)
    return results