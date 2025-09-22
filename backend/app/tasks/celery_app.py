from celery import Celery
from app.core.config import config
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from redis.asyncio import Redis as AsyncRedis
from motor.motor_asyncio import AsyncIOMotorClient
from app.domain.llm_summarization.models.llm_summarization_model import ArticleDoc
from app.adapters.cache.keys import k_art_tldr
from app.adapters.cache.json import cache_get_json, cache_set_json
from app.utils.helpers import compute_article_hash
from app.domain.llm_summarization.services.llm_routines import quick_tldr_bullets

import asyncio
from datetime import datetime, timezone
from app.domain.llm_summarization.services.llm_routines import summarize_article_text
from app.adapters.cache.keys import MODEL, PVER
import hashlib
from typing import Dict, Any, List, Tuple
import json



celery_app = Celery(
    __name__, broker=config.CELERY_BROKER_URL, backend=config.CELERY_RESULT_BACKEND
)

# We keep Celery tasks simple; they re-open their own clients


def _new_llm() -> ChatOpenAI:
    return ChatOpenAI(api_key=config.OPENAI_API_KEY, model=config.OPENAI_MODEL, temperature=0)


def _new_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=config.SUMMARY_MAP_CHUNK_SIZE,
        chunk_overlap=config.SUMMARY_MAP_CHUNK_OVERLAP,
    )

@celery_app.task(name="summarize_article", queue="default", max_retries=3, autoretry_for=(Exception,), retry_backoff=5)
def summarize_article_task(article_id: str) -> str:
    """Blocking Celery task: summarize a single article idempotently.
    Returns the Redis per-article cache key that was set.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)


    async def _run() -> str:
        mongo = AsyncIOMotorClient(config.MONGO_URI)[config.MONGO_DB]
        redis = AsyncRedis.from_url(config.REDIS_URL, decode_responses=True)
        try:
            raw = await mongo.articles.find_one({"_id": article_id})
            if not raw:
                return ""
            
            art = ArticleDoc.model_validate(raw)
            if not art.content or not art.content.strip():
                return ""
            h = await compute_article_hash(art)
            # Check Redis memo
            memo = await cache_get_json(redis, k_art_sum(art.id))
            if memo and memo.get("summary_hash") == h:
                await redis.set(k_art_hash(art.id), h)
                return k_art_sum(art.id)


            # Compute
            summary = await summarize_article_text(_new_llm(), _new_splitter(), title=art.title or "", url=art.url, content=art.content, n_map_bullets=settings.SUMMARY_BULLET_TARGET)


            # Persist to Mongo and Redis
            await mongo.articles.update_one({"_id": art.id}, {"$set": {"summary_ai": summary, "summary_hash": h}})
            await cache_set_json(redis, k_art_sum(art.id), {"summary": summary, "summary_hash": h, "article_id": art.id, "model": MODEL, "pver": PVER, "created_at": datetime.now(timezone.utc).isoformat()})
            await redis.set(k_art_hash(art.id), h)
            return k_art_sum(art.id)
        finally:
            await redis.close()
            mongo.client.close()


    return loop.run_until_complete(_run())

@celery_app.task(name="generate_tldr", queue="low", max_retries=3, autoretry_for=(Exception,), retry_backoff=5)
def generate_tldr_task(article_id: str) -> str:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)


    async def _run() -> str:
        mongo = AsyncIOMotorClient(config.MONGO_URI)[config.MONGO_DB]
        redis = AsyncRedis.from_url(config.REDIS_URL, decode_responses=True)
        try:
            raw = await mongo.articles.find_one({"_id": article_id}, projection={"_id": 1, "content": 1})
            if not raw:
                return ""
            art = ArticleDoc.model_validate(raw)
            if not art.content or not art.content.strip():
                return ""
            memo = await redis.get(k_art_tldr(art.id))
            if memo:
                return k_art_tldr(art.id)
            tldr = await quick_tldr_bullets(_new_llm(), _new_splitter(), content=art.content, n_bullets=3)
            await redis.set(k_art_tldr(art.id), tldr, ex=7 * 24 * 3600)
            return k_art_tldr(art.id)
        finally:
            await redis.close()
            mongo.client.close()


    return loop.run_until_complete(_run())

@celery_app.task(name="build_category_brief", queue="high", max_retries=3, autoretry_for=(Exception,), retry_backoff=5)
def build_category_brief_task(category: str, since_iso: str, until_iso: str) -> str:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)


    async def _run() -> str:
        mongo = AsyncIOMotorClient(config.MONGO_URI)[config.MONGO_DB]
        redis = AsyncRedis.from_url(config.REDIS_URL, decode_responses=True)
        try:
            # Build aggregate list (ids + hashes)
            q: Dict[str, Any] = {"category": category, "published_at": {"$gte": datetime.fromisoformat(since_iso), "$lte": datetime.fromisoformat(until_iso)}}
            cursor = mongo.articles.find(q, projection={"_id": 1, "summary_hash": 1, "content": 1, "source": 1, "title": 1}).sort("published_at", -1).limit(settings.CATEGORY_MAX_ARTICLES)
            ids: List[str] = []
            pairs: List[Tuple[str, str]] = []
            bullets: List[str] = []


            splitter = _new_splitter()
            llm = _new_llm()


            async for d in cursor:
                _id = str(d.get("_id"))
                ids.append(_id)
                h = d.get("summary_hash") or stable_hash(d.get("content") or "")
                pairs.append((_id, h))
                # TL;DR bullets (prefer cache)
                b = await redis.get(k_art_tldr(_id))
                if not b:
                    content = d.get("content") or ""
                if content:
                    b = await quick_tldr_bullets(llm, splitter, content=content, n_bullets=3)
                await redis.set(k_art_tldr(_id), b, ex=7 * 24 * 3600)
                if b:
                    bullets.append(b)


            # Aggregate hash
            pairs.sort(key=lambda x: x[0])
            agg_str = "|".join(f"{i}:{h}" for i, h in pairs)
            agg_hash = hashlib.sha256(agg_str.encode("utf-8")).hexdigest()


            # Fresh brief via reducer
            brief = await reduce_category_long_brief(llm, category=category, since_iso=since_iso, until_iso=until_iso, bullets_lines=bullets)
            brief.article_count = len(ids)
            payload = json.loads(brief.model_dump_json())


            await cache_set_json(redis, k_cat_brief(category, since_iso, until_iso), payload)
            await redis.set(k_cat_agg(category, since_iso, until_iso), agg_hash)
            return k_cat_brief(category, since_iso, until_iso)
        finally:
            await redis.close()
            mongo.client.close()


    return loop.run_until_complete(_run())