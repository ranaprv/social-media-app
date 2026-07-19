"""Content Series Manager — multi-part threads, weekly series, campaign arcs.

Manages sequential content that forms a narrative across multiple posts.
"""
import logging
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Series templates
SERIES_TEMPLATES = {
    "weekly_thread": {
        "name": "Weekly Thread Series",
        "frequency": "weekly",
        "parts": 4,
        "platforms": ["x", "linkedin"],
        "description": "4-part series on a topic, released weekly",
    },
    "daily_tip": {
        "name": "Daily Tips Series",
        "frequency": "daily",
        "parts": 7,
        "platforms": ["linkedin", "x"],
        "description": "7 consecutive daily tips on a theme",
    },
    "case_study_series": {
        "name": "Case Study Series",
        "frequency": "weekly",
        "parts": 3,
        "platforms": ["linkedin", "facebook"],
        "description": "3-part deep dive case study",
    },
    "behind_scenes_arc": {
        "name": "Behind the Scenes Arc",
        "frequency": "weekly",
        "parts": 5,
        "platforms": ["instagram", "facebook"],
        "description": "5-week journey showing your process",
    },
    "tutorial_series": {
        "name": "Tutorial Series",
        "frequency": "weekly",
        "parts": 6,
        "platforms": ["youtube", "linkedin"],
        "description": "6-part tutorial series",
    },
}


async def create_content_series(
    db: AsyncSession,
    workspace_id: str,
    name: str,
    topic: str,
    template: str = "weekly_thread",
    platforms: list[str] | None = None,
    total_parts: int | None = None,
) -> dict[str, Any]:
    """Create a new content series."""
    from app.models.content import Activity

    tmpl = SERIES_TEMPLATES.get(template, SERIES_TEMPLATES["weekly_thread"])
    series_id = str(uuid.uuid4())

    activity = Activity(
        id=str(uuid.uuid4()),
        user_id="system",
        type="series_created",
        description=f"Content series created: {name}",
        meta={
            "series_id": series_id,
            "name": name,
            "topic": topic,
            "template": template,
            "total_parts": total_parts or tmpl["parts"],
        },
    )
    db.add(activity)
    await db.flush()

    return {
        "series_id": series_id,
        "name": name,
        "topic": topic,
        "template": template,
        "total_parts": total_parts or tmpl["parts"],
        "platforms": platforms or tmpl["platforms"],
        "frequency": tmpl["frequency"],
        "status": "active",
        "parts_created": 0,
    }


def get_series_templates() -> list[dict[str, Any]]:
    """Get available series templates."""
    return [
        {"key": k, **v}
        for k, v in SERIES_TEMPLATES.items()
    ]
