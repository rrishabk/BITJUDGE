from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.db.session import get_redis


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in {"/health", "/docs", "/openapi.json", "/redoc"}:
            return await call_next(request)

        redis = get_redis()
        if redis is None:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"rate-limit:{client_ip}:{request.url.path}"
        window = settings.rate_limit_window_seconds
        limit = settings.rate_limit_requests

        current = await redis.incr(key)
        if current == 1:
            await redis.expire(key, window)

        remaining = max(limit - current, 0)
        ttl = await redis.ttl(key)
        if current > limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": str(max(ttl, 0)),
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
