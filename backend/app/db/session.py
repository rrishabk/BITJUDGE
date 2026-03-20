import os
from collections.abc import AsyncGenerator

from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings

_engine = None
_session_factory = None
redis_client: Redis | None = None


def _build_engine_kwargs() -> dict[str, object]:
    engine_kwargs: dict[str, object] = {
        "echo": False,
        "pool_pre_ping": True,
    }

    if os.getenv("VERCEL") or os.getenv("VERCEL_ENV"):
        engine_kwargs["poolclass"] = NullPool
    else:
        engine_kwargs["pool_size"] = settings.db_pool_size
        engine_kwargs["max_overflow"] = settings.db_max_overflow
        engine_kwargs["pool_timeout"] = settings.db_pool_timeout
        engine_kwargs["pool_recycle"] = settings.db_pool_recycle

    return engine_kwargs


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(settings.sqlalchemy_database_uri, **_build_engine_kwargs())
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(get_engine(), class_=AsyncSession, expire_on_commit=False)
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    try:
        session_factory = get_session_factory()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not configured correctly",
        ) from exc

    async with session_factory() as session:
        yield session


async def init_redis() -> None:
    global redis_client
    if redis_client is None and settings.redis_url:
        try:
            redis_client = Redis.from_url(
                settings.redis_url,
                decode_responses=True,
                max_connections=settings.redis_max_connections,
                health_check_interval=30,
            )
        except Exception:
            redis_client = None


async def close_redis() -> None:
    global redis_client
    if redis_client is not None:
        await redis_client.aclose()
        redis_client = None


def get_redis() -> Redis | None:
    return redis_client
