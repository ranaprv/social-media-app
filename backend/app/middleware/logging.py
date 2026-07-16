"""Request/response logging middleware."""
import logging
import time
from fastapi import Request

logger = logging.getLogger("socialmediamanager.api")


async def log_requests(request: Request, call_next):
    """Log API requests with method, path, status, and duration."""
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000

    logger.info(
        f"{request.method} {request.url.path} "
        f"status={response.status_code} "
        f"duration={duration:.1f}ms"
    )
    return response
