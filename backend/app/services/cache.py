import json
from typing import Any

from app.db.session import get_redis


async def cache_json(key: str, value: Any, ttl: int = 300) -> None:
    redis = get_redis()
    if redis is not None:
        await redis.set(key, json.dumps(value), ex=ttl)


async def get_cached_json(key: str) -> Any | None:
    redis = get_redis()
    if redis is None:
        return None
    value = await redis.get(key)
    return json.loads(value) if value else None


async def delete_cache_keys(*keys: str) -> None:
    redis = get_redis()
    if redis is not None and keys:
        await redis.delete(*keys)


async def delete_cache_prefix(prefix: str) -> None:
    redis = get_redis()
    if redis is None:
        return

    cursor = 0
    pattern = f"{prefix}*"
    keys_to_delete: list[str] = []
    while True:
        cursor, keys = await redis.scan(cursor=cursor, match=pattern, count=100)
        keys_to_delete.extend(keys)
        if cursor == 0:
            break
    if keys_to_delete:
        await redis.delete(*keys_to_delete)
