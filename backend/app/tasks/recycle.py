"""Celery task for auto-recycling top performers.

Runs weekly to find and schedule recycling of top-performing posts.
"""
import logging
from app.tasks import celery_app

logger = logging.getLogger(__name__)


@celery_app.task
def auto_recycle_posts():
    """Find top performers across all workspaces and schedule recycles."""
    logger.info("Running auto-recycle for top performers...")

    try:
        import asyncio
        from sqlalchemy import select
        from app.core.database import AsyncSessionLocal
        from app.models.workspace import Workspace
        from app.services.content_recycler import auto_recycle_top_performers

        async def _recycle():
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(Workspace))
                workspaces = result.scalars().all()
                total_scheduled = 0

                for ws in workspaces:
                    scheduled = await auto_recycle_top_performers(
                        db=db,
                        workspace_id=ws.id,
                        max_recycles_per_week=2,
                    )
                    total_scheduled += len(scheduled)
                    if scheduled:
                        logger.info(
                            f"Workspace {ws.id}: scheduled {len(scheduled)} recycles"
                        )

                await db.commit()
                return total_scheduled

        count = asyncio.run(_recycle())
        logger.info(f"Auto-recycle complete: {count} posts scheduled")
        return {"recycled": count}

    except Exception as e:
        logger.error(f"Auto-recycle task failed: {e}")
        return {"error": str(e)}
