"""UGC Campaign Builder — create branded hashtag campaigns, curate submissions.

Manages user-generated content campaigns from creation to curation.
"""
import logging
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def create_ugc_campaign(
    db: AsyncSession,
    workspace_id: str,
    name: str,
    branded_hashtag: str,
    description: str = "",
    platforms: list[str] | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    rules: str = "",
) -> dict[str, Any]:
    """Create a UGC campaign."""
    from app.models.content import Activity

    campaign_id = str(uuid.uuid4())
    activity = Activity(
        id=str(uuid.uuid4()),
        user_id="system",
        type="ugc_campaign_created",
        description=f"UGC campaign created: {name}",
        meta={
            "campaign_id": campaign_id,
            "name": name,
            "branded_hashtag": branded_hashtag,
            "platforms": platforms or ["instagram"],
        },
    )
    db.add(activity)
    await db.flush()

    return {
        "campaign_id": campaign_id,
        "name": name,
        "branded_hashtag": branded_hashtag,
        "description": description,
        "platforms": platforms or ["instagram"],
        "status": "active",
        "start_date": start_date,
        "end_date": end_date,
        "rules": rules,
    }


async def get_ugc_submissions(
    branded_hashtag: str,
    platform: str | None = None,
) -> dict[str, Any]:
    """Get UGC submissions for a campaign (placeholder)."""
    return {
        "hashtag": branded_hashtag,
        "submissions": [],
        "total": 0,
        "message": "Connect platform APIs to fetch real submissions",
    }


def get_ugc_best_practices() -> list[dict[str, str]]:
    """Get UGC campaign best practices."""
    return [
        {"tip": "Keep the hashtag short and memorable", "importance": "high"},
        {"tip": "Offer clear incentives for participation", "importance": "high"},
        {"tip": "Feature the best submissions prominently", "importance": "high"},
        {"tip": "Always ask permission before reposting", "importance": "high"},
        {"tip": "Create a clear content brief for participants", "importance": "medium"},
        {"tip": "Cross-promote the campaign across all platforms", "importance": "medium"},
        {"tip": "Track submissions with a unique hashtag", "importance": "medium"},
        {"tip": "Engage with every submission (like, comment, share)", "importance": "medium"},
    ]
