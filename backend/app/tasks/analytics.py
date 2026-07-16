"""Celery task to collect analytics from social platforms."""
import logging
from app.tasks import celery_app

logger = logging.getLogger(__name__)


@celery_app.task
def collect_all_analytics():
    """Collect analytics for all workspaces with connected platforms."""
    logger.info("Starting analytics collection for all workspaces...")

    try:
        import asyncio
        from sqlalchemy import select
        from app.core.database import AsyncSessionLocal
        from app.models.workspace import Workspace
        from app.services.analytics_collector import collect_analytics_for_workspace

        async def _collect():
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(Workspace))
                workspaces = result.scalars().all()
                for ws in workspaces:
                    await collect_analytics_for_workspace(ws.id)
                return len(workspaces)

        count = asyncio.run(_collect())
        logger.info(f"Analytics collection complete for {count} workspaces")
        return {"workspaces_processed": count}

    except Exception as e:
        logger.error(f"Analytics collection task failed: {e}")
        return {"error": str(e)}
