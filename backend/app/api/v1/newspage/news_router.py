from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime, timedelta, timezone
from app.services import cache, db, rank


router = APIRouter()


VALID_TABS = {"general","ai","ipos","smallcaps","macro"}
VALID_SINCE = {"today","24h","7d"}
VALID_SENT = {"any","bull","bear","neutral"}


@router.get("")
async def list_news(
    tab: str = Query("general"),
    since: str = Query("24h"),
    sentiment: str = Query("any"),
    sources: str = Query("all"),
    limit: int = Query(50, ge=1, le=200),
    watchlist: Optional[str] = None,
    cursor: Optional[str] = None,
    ):

    if tab not in VALID_TABS:
        raise HTTPException(status_code=400, detail={"code":"INVALID_PARAM","message":"invalid tab"})
    if since not in VALID_SINCE:
        raise HTTPException(status_code=400, detail={"code":"INVALID_PARAM","message":"invalid since"})
    if sentiment not in VALID_SENT:
        raise HTTPException(status_code=400, detail={"code":"INVALID_PARAM","message":"invalid sentiment"})


    now = datetime.now(timezone.utc)
    cutoff = {
    "today": datetime(now.year, now.month, now.day),
    "24h": now - timedelta(hours=24),
    "7d": now - timedelta(days=7),
    }[since]


    wl = [t.strip().upper() for t in watchlist.split(",")] if watchlist else []


    cache_key = f"news:{tab}:{since}:{sentiment}:{sources}:{','.join(wl) or 'none'}:{limit}:{cursor or '0'}"
    cached = await cache.get(cache_key)
    if cached:
        return cached


    # Query DB and rank
    articles = await db.query_articles(tab=tab, cutoff=cutoff, sentiment=sentiment, sources=sources, limit=limit, watchlist=wl, cursor=cursor)
    ranked = rank.rank_articles(articles)


    result = {
    "tab": tab,
    "window": since,
    "generated_at": now.isoformat() + "Z",
    "next_cursor": None, # stubbed
    "articles": [a.dict() for a in ranked[:limit]],
    }

    await cache.set(cache_key, result, ttl=900)
    return result