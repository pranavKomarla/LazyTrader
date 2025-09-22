import json
from typing import Any
from redis.asyncio import Redis as AsyncRedis


# Redis cache helper functions for JSON
async def cache_set_json(r: AsyncRedis, key: str, obj: Any, ttl: int | None = None):
    s = json.dumps(obj, default=str, separators=(",", ":"))
    if ttl:
        await r.set(key, s, ex=ttl)
    else:
        await r.set(key, s)


async def cache_get_json(r: AsyncRedis, key: str) -> Any | None:
    s = await r.get(key)
    return None if s is None else json.loads(s)