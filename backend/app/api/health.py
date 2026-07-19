"""Health check endpoints — liveness and readiness probes.

Provides Kubernetes-compatible health checks for PostgreSQL, Redis, and Celery.
"""
import logging
import time
from datetime import datetime

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Basic liveness check — is the service running?"""
    return {
        "status": "healthy",
        "service": "social-media-manager-api",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/health/ready")
async def readiness_check():
    """Readiness check — is the service ready to accept traffic?

    Checks PostgreSQL, Redis, and Celery connectivity.
    """
    checks = {}
    overall_status = "ready"

    # Check PostgreSQL
    try:
        from app.core.database import AsyncSessionLocal
        from sqlalchemy import text

        start = time.time()
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        duration = round((time.time() - start) * 1000, 1)
        checks["postgresql"] = {"status": "healthy", "latency_ms": duration}
    except Exception as e:
        checks["postgresql"] = {"status": "unhealthy", "error": str(e)}
        overall_status = "degraded"

    # Check Redis
    try:
        from app.core.config import get_settings
        settings = get_settings()

        start = time.time()
        import redis.asyncio as aioredis
        async with aioredis.from_url(settings.REDIS_URL, socket_timeout=3) as r:
            await r.ping()
        duration = round((time.time() - start) * 1000, 1)
        checks["redis"] = {"status": "healthy", "latency_ms": duration}
    except Exception as e:
        checks["redis"] = {"status": "unhealthy", "error": str(e)}
        overall_status = "degraded"

    # Check Celery (inspect active tasks)
    try:
        from app.tasks import celery_app
        start = time.time()
        inspector = celery_app.control.inspect(timeout=2)
        active = inspector.active() or {}
        duration = round((time.time() - start) * 1000, 1)
        total_active = sum(len(tasks) for tasks in active.values())
        checks["celery"] = {
            "status": "healthy",
            "latency_ms": duration,
            "active_tasks": total_active,
            "workers": len(active),
        }
    except Exception as e:
        checks["celery"] = {"status": "unhealthy", "error": str(e)}
        overall_status = "degraded"

    status_code = 200 if overall_status == "ready" else 503

    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks,
    }


@router.get("/health/deep")
async def deep_health_check():
    """Deep health check — comprehensive system status.

    Includes connection pool stats, memory usage, and queue depth.
    """
    result = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
    }

    # Database pool stats
    try:
        from app.core.database import engine
        pool = engine.pool
        result["database"] = {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
        }
    except Exception as e:
        result["database"] = {"error": str(e)}

    # Queue depth
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.post_platform import PostPlatform
        from sqlalchemy import select, func

        async with AsyncSessionLocal() as session:
            scheduled = await session.execute(
                select(func.count(PostPlatform.id)).where(
                    PostPlatform.status == "scheduled"
                )
            )
            publishing = await session.execute(
                select(func.count(PostPlatform.id)).where(
                    PostPlatform.status == "publishing"
                )
            )
            failed = await session.execute(
                select(func.count(PostPlatform.id)).where(
                    PostPlatform.status == "failed"
                )
            )
            result["queue"] = {
                "scheduled": scheduled.scalar() or 0,
                "publishing": publishing.scalar() or 0,
                "failed": failed.scalar() or 0,
            }
    except Exception as e:
        result["queue"] = {"error": str(e)}

    # Circuit breaker status
    try:
        from app.middleware.circuit_breaker import get_all_breakers
        result["circuit_breakers"] = get_all_breakers()
    except Exception as e:
        result["circuit_breakers"] = {"error": str(e)}

    return result
