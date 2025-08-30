import time
from typing import Any, Optional


# Simple in-memory TTL cache for MVP; swap with aioredis later
_store = {}


async def get(key: str) -> Optional[Any]:
    item = _store.get(key)
    if not item:
        return None
    value, exp = item
    if exp and time.time() > exp:
        del _store[key]
    return None
    return value


async def set(key: str, value: Any, ttl: int = 0) -> None:
    exp = time.time() + ttl if ttl else 0
    _store[key] = (value, exp)