"""
Rate limiting middleware using Redis as backend.
Provides per-IP and per-endpoint rate limiting.
"""

import time
from typing import Optional, Callable
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis

from app.core.config import settings


class RateLimiter:
    """Redis-based rate limiter using sliding window."""

    def __init__(self):
        try:
            self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
            self.redis.ping()
            self.enabled = True
        except Exception:
            self.enabled = False

    def is_rate_limited(self, key: str, max_requests: int, window_seconds: int) -> tuple[bool, dict]:
        """
        Check if a key has exceeded rate limit.
        Returns (is_limited, info_dict).
        """
        if not self.enabled:
            return False, {}

        now = time.time()
        window_start = now - window_seconds
        pipe = self.redis.pipeline()

        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start)
        # Add current request
        pipe.zadd(key, {str(now): now})
        # Count requests in window
        pipe.zcard(key)
        # Set expiry on key
        pipe.expire(key, window_seconds + 1)

        results = pipe.execute()
        request_count = results[2]

        info = {
            "X-RateLimit-Limit": str(max_requests),
            "X-RateLimit-Remaining": str(max(0, max_requests - request_count)),
            "X-RateLimit-Reset": str(int(now + window_seconds)),
        }

        return request_count > max_requests, info


# Singleton
rate_limiter = RateLimiter()


# Route-specific rate limit configs
RATE_LIMITS = {
    "/api/v1/auth/login": {"max_requests": 5, "window_seconds": 60},  # 5 per minute
    "/api/v1/auth/login/json": {"max_requests": 5, "window_seconds": 60},
    "/api/v1/generation/run": {"max_requests": 20, "window_seconds": 60},  # 20 per minute
    "/api/v1/generation/regenerate": {"max_requests": 20, "window_seconds": 60},
}

# Default rate limit for all API endpoints
DEFAULT_RATE_LIMIT = {"max_requests": 100, "window_seconds": 60}  # 100 per minute


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting."""

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks and non-API routes
        path = request.url.path
        if path in ["/health", "/health/detailed"] or not path.startswith("/api/"):
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()

        # Determine rate limit for this path
        config = RATE_LIMITS.get(path, DEFAULT_RATE_LIMIT)

        # Build rate limit key
        key = f"ratelimit:{client_ip}:{path}"

        # Check rate limit
        is_limited, info = rate_limiter.is_rate_limited(
            key, config["max_requests"], config["window_seconds"]
        )

        if is_limited:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests. Please try again later."},
                headers=info,
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        for header, value in info.items():
            response.headers[header] = value

        return response
