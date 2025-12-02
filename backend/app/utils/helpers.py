import hashlib
from datetime import datetime, timezone
from app.adapters.cache.keys import MODEL, PVER


# Helper functions

def stable_hash(text: str) -> str:
    # Include model + prompt version to force cache-busts when you change them
    salt = f"{MODEL}|{PVER}|"
    return hashlib.sha256((salt + (text or "")).encode("utf-8")).hexdigest()


async def compute_article_hash(article: ArticleDoc) -> str:
    return stable_hash(article.content)


async def to_iso(dt: datetime | None) -> str:
    if not dt:
        return ""

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat()