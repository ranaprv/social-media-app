"""FastAPI application — Social Media Manager API.

Production-ready with:
  - Structured JSON logging
  - Request ID propagation
  - Rate limiting
  - Circuit breakers for external APIs
  - Graceful shutdown
  - Health checks
"""
import logging
import signal
import sys

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.logging_config import setup_logging, request_id_var

settings = get_settings()

# ─── Logging Setup ──────────────────────────────────────────────────────────
setup_logging(level="INFO", json_output=(settings.ENVIRONMENT == "production"))
logger = logging.getLogger(__name__)

# ─── App Creation ───────────────────────────────────────────────────────────
app = FastAPI(
    title="Social Media Manager API",
    description="AI-Powered Social Media Content Management Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ─── Middleware (order matters — last added = first executed) ────────────────

# 1. Request ID (generates correlation ID for every request)
from app.middleware.request_id import RequestIDMiddleware
app.add_middleware(RequestIDMiddleware)

# 2. Rate Limiting
from app.middleware.rate_limiter import RateLimiterMiddleware
app.add_middleware(RateLimiterMiddleware)

# 3. CORS
allowed_origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 4. Security Headers
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if settings.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; font-src 'self' https://fonts.gstatic.com"
        )
    return response


# 5. Request Logging with structured fields
@app.middleware("http")
async def structured_logging(request: Request, call_next):
    import time
    start = time.time()
    request_id = getattr(request.state, "request_id", "")

    response = await call_next(request)

    duration_ms = round((time.time() - start) * 1000, 1)
    logger.info(
        f"{request.method} {request.url.path} → {response.status_code}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    return response


# ─── Routes ─────────────────────────────────────────────────────────────────

# Health checks
from app.api.health import router as health_router
app.include_router(health_router, prefix="/api")

# API routes
from app.api import (
    auth, workspaces, posts, dashboard, connections,
    ai_content, ai_ideas, ai_writing_tools, ai_brand_voice,
    repurpose, calendar, scheduler_api, team, media,
    analytics, billing, security_api, recommendations, ai_media,
    webhooks, research, bulk_scheduler, inbox, listening,
    automation, tasks, competitors, reports, ads, web_analytics,
    approvals, advocacy, ai_workflow, ai_models, ai_keys,
    connections_callback, strategies, content_generation,
)

app.include_router(auth.router, prefix="/api")
app.include_router(workspaces.router, prefix="/api")
app.include_router(posts.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(connections.router, prefix="/api")
app.include_router(ai_content.router, prefix="/api")
app.include_router(ai_ideas.router, prefix="/api")
app.include_router(ai_writing_tools.router, prefix="/api")
app.include_router(ai_brand_voice.router, prefix="/api")
app.include_router(repurpose.router, prefix="/api")
app.include_router(calendar.router, prefix="/api")
app.include_router(scheduler_api.router, prefix="/api")
app.include_router(team.router, prefix="/api")
app.include_router(media.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(billing.router, prefix="/api")
app.include_router(security_api.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(ai_media.router, prefix="/api")
app.include_router(webhooks.router, prefix="/api")
app.include_router(research.router, prefix="/api")
app.include_router(bulk_scheduler.router, prefix="/api")
app.include_router(inbox.router, prefix="/api")
app.include_router(listening.router, prefix="/api")
app.include_router(automation.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(competitors.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(ads.router, prefix="/api")
app.include_router(web_analytics.router, prefix="/api")
app.include_router(approvals.router, prefix="/api")
app.include_router(advocacy.router, prefix="/api")
app.include_router(ai_workflow.router, prefix="/api")
app.include_router(ai_models.router, prefix="/api")
app.include_router(ai_keys.router, prefix="/api")
app.include_router(connections_callback.router, prefix="/api")
app.include_router(strategies.router, prefix="/api")
app.include_router(content_generation.router, prefix="/api")


# ─── Graceful Shutdown ──────────────────────────────────────────────────────

@app.on_event("shutdown")
async def shutdown():
    """Clean up resources on shutdown."""
    logger.info("Shutting down application...")

    # Dispose database connection pool
    try:
        from app.core.database import dispose_engine
        await dispose_engine()
        logger.info("Database connection pool disposed")
    except Exception as e:
        logger.error(f"Error disposing database pool: {e}")

    # Shutdown Celery workers
    try:
        from app.tasks import celery_app
        celery_app.control.shutdown()
        logger.info("Celery workers shut down")
    except Exception as e:
        logger.error(f"Error shutting down Celery: {e}")

    logger.info("Shutdown complete")


@app.on_event("startup")
async def startup():
    """Initialize services on startup."""
    logger.info(
        f"Starting Social Media Manager API v1.0.0 "
        f"(env={settings.ENVIRONMENT})"
    )

    # Verify database connection
    try:
        from app.core.database import AsyncSessionLocal
        from sqlalchemy import text
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        logger.info("Database connection verified")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")

    # Verify Redis connection
    try:
        import redis.asyncio as aioredis
        async with aioredis.from_url(settings.REDIS_URL, socket_timeout=3) as r:
            await r.ping()
        logger.info("Redis connection verified")
    except Exception as e:
        logger.warning(f"Redis connection failed (non-critical): {e}")

    logger.info("Application ready")
