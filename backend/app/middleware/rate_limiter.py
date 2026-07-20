"""Rate limiter middleware — per-user, per-endpoint rate limiting.

Uses sliding window algorithm with Redis backend.
Falls back to in-memory if Redis is unavailable.
"""
import os
import time
import logging
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

# Skip rate limiting in test mode
SKIP_RATE_LIMITING = os.environ.get("TESTING") == "1" or os.environ.get("DATABASE_URL", "").startswith("sqlite")

# In-memory fallback storage
_memory_store: dict[str, list[float]] = defaultdict(list)

# Default limits: requests per window
DEFAULT_LIMITS = {
    "global": {"requests": 100, "window": 60},  # 100 req/min
    "auth": {"requests": 10, "window": 60},      # 10 req/min for auth
    "ai": {"requests": 20, "window": 60},         # 20 req/min for AI
    "publish": {"requests": 5, "window": 60},     # 5 req/min for publishing
}

# Path to limit category mapping
PATH_LIMITS = {
    "/api/auth/": "auth",
    "/api/scheduler/captions/": "ai",
    "/api/scheduler/hashtags/": "ai",
    "/api/scheduler/repurpose": "ai",
    "/api/scheduler/translate": "ai",
    "/api/scheduler/calendar/generate": "ai",
    "/api/scheduler/forecast": "ai",
    "/api/scheduler/quality/score": "ai",
    "/api/scheduler/schedule": "publish",
    "/api/scheduler/ab-test/": "publish",
}


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Sliding window rate limiter."""

    def __init__(self, app, redis_client=None):
        super().__init__(app)
        self.redis = redis_client

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting in test mode
        if SKIP_RATE_LIMITING:
            return await call_next(request)

        # Skip rate limiting for health checks and docs
        path = request.url.path
        if path in ("/api/health", "/api/docs", "/api/redoc", "/openapi.json"):
            return await call_next(request)

        # Get client identifier
        client_id = self._get_client_id(request)

        # Determine rate limit category
        category = "global"
        for prefix, cat in PATH_LIMITS.items():
            if path.startswith(prefix):
                category = cat
                break

        limit_config = DEFAULT_LIMITS.get(category, DEFAULT_LIMITS["global"])

        # Check rate limit
        allowed, remaining, reset_at = self._check_rate_limit(
            client_id, category, limit_config
        )

        if not allowed:
            retry_after = max(1, int(reset_at - time.time()))
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Retry after {retry_after}s.",
                    "retry_after": retry_after,
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit_config["requests"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(reset_at)),
                },
            )

        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(limit_config["requests"])
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(reset_at))

        return response

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier (user ID or IP)."""
        # Try to get user ID from auth header
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            try:
                from app.core.security import decode_token
                token = auth[7:]
                payload = decode_token(token)
                user_id = payload.get("sub", "")
                if user_id:
                    return f"user:{user_id}"
            except Exception:
                pass

        # Fallback to IP
        forwarded = request.headers.get("X-Forwarded-For", "")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        return f"ip:{ip}"

    def _check_rate_limit(
        self, client_id: str, category: str, config: dict
    ) -> tuple[bool, int, float]:
        """Check rate limit using sliding window. Returns (allowed, remaining, reset_at)."""
        now = time.time()
        window = config["window"]
        max_requests = config["requests"]
        key = f"ratelimit:{client_id}:{category}"

        # Try Redis first
        if self.redis:
            try:
                return self._check_redis(key, now, window, max_requests)
            except Exception as e:
                logger.warning(f"Redis rate limit failed, using memory: {e}")

        # Fallback to in-memory
        return self._check_memory(key, now, window, max_requests)

    def _check_redis(self, key: str, now: float, window: int, max_requests: int) -> tuple[bool, int, float]:
        """Check rate limit using Redis sorted sets."""
        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, 0, now - window)
        pipe.zadd(key, {str(now): now})
        pipe.zcard(key)
        pipe.expire(key, window)
        results = pipe.execute()

        count = results[2]
        remaining = max(0, max_requests - count)
        reset_at = now + window

        return count <= max_requests, remaining, reset_at

    def _check_memory(self, key: str, now: float, window: int, max_requests: int) -> tuple[bool, int, float]:
        """Check rate limit using in-memory sliding window."""
        timestamps = _memory_store[key]

        # Remove expired entries
        _memory_store[key] = [t for t in timestamps if t > now - window]

        count = len(_memory_store[key])
        remaining = max(0, max_requests - count)
        reset_at = now + window

        if count < max_requests:
            _memory_store[key].append(now)

        return count < max_requests, remaining, reset_at
