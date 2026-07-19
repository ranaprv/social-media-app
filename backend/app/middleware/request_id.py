"""Request ID middleware — generates and propagates correlation IDs.

Every request gets a unique ID that flows through logs and responses.
"""
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging_config import request_id_var


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to every request/response cycle."""

    async def dispatch(self, request: Request, call_next):
        # Get existing request ID or generate new one
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Set context variable for logging
        token = request_id_var.set(request_id)
        request.state.request_id = request_id

        # Track timing
        start_time = time.time()

        try:
            response = await call_next(request)
        except Exception:
            # Re-raise after cleanup
            request_id_var.reset(token)
            raise

        # Calculate duration
        duration_ms = round((time.time() - start_time) * 1000, 1)

        # Add headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration_ms}ms"

        # Reset context
        request_id_var.reset(token)

        return response
