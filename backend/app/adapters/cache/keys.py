# Redis key helpers

from app.core.config import config

PVER = config.PROMPT_VERSION
MODEL = config.OPENAI_MODEL

def k_art_sum(article_id: str) -> str: # cached per-article summary JSON (with summary + hash).
    return f"art:sum:{article_id}:{MODEL}:{PVER}"

def k_art_hash(article_id: str) -> str: # last known content hash (quick "did content change?" check).
    return f"art:hash:{article_id}"

def k_art_tldr(article_id: str) -> str: # small TL;DR bullets string for use in digests.
    return f"art:tldr:{article_id}:{MODEL}:{PVER}"

def k_cat_brief(category: str, since: str, until: str) -> str: # structured JSON for a category window. 
    return f"cat:brief:{category}:{since}:{until}:{MODEL}:{PVER}"

def k_cat_agg(category: str, since: str, until: str) -> str: # aggregate hash used to validate the cat:brief cache.
    return f"cat:agg:{category}:{since}:{until}:{MODEL}:{PVER}"
