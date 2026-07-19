"""Campaign Calendar — cross-platform content calendar with campaign arcs.

Manages multi-platform campaigns with coordinated content schedules.
"""
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

CAMPAIGN_TYPES = {
    "product_launch": {
        "name": "Product Launch",
        "phases": [
            {"name": "Teaser", "duration_days": 7, "content_focus": "curiosity, behind-the-scenes"},
            {"name": "Launch", "duration_days": 3, "content_focus": "announcement, features, demo"},
            {"name": "Social Proof", "duration_days": 7, "content_focus": "testimonials, reviews, results"},
            {"name": "Sustain", "duration_days": 14, "content_focus": "tips, use cases, community"},
        ],
        "platforms": ["linkedin", "x", "instagram", "facebook", "youtube"],
    },
    "brand_awareness": {
        "name": "Brand Awareness",
        "phases": [
            {"name": "Introduction", "duration_days": 14, "content_focus": "brand story, values, mission"},
            {"name": "Education", "duration_days": 21, "content_focus": "industry expertise, thought leadership"},
            {"name": "Engagement", "duration_days": 14, "content_focus": "community building, UGC, polls"},
        ],
        "platforms": ["linkedin", "instagram", "youtube"],
    },
    "lead_generation": {
        "name": "Lead Generation",
        "phases": [
            {"name": "Awareness", "duration_days": 14, "content_focus": "pain points, industry trends"},
            {"name": "Consideration", "duration_days": 14, "content_focus": "solutions, case studies, webinars"},
            {"name": "Conversion", "duration_days": 7, "content_focus": "offers, demos, trials, CTAs"},
        ],
        "platforms": ["linkedin", "facebook", "youtube"],
    },
}


async def create_campaign(
    db: AsyncSession,
    workspace_id: str,
    name: str,
    campaign_type: str = "product_launch",
    start_date: str | None = None,
    platforms: list[str] | None = None,
    goals: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a campaign with coordinated content schedule."""
    from app.models.content import Activity

    template = CAMPAIGN_TYPES.get(campaign_type, CAMPAIGN_TYPES["product_launch"])
    campaign_id = str(uuid.uuid4())

    # Calculate dates
    start = datetime.fromisoformat(start_date) if start_date else datetime.utcnow()
    total_days = sum(p["duration_days"] for p in template["phases"])

    # Build phase schedule
    phases = []
    current_date = start
    for phase in template["phases"]:
        end_date = current_date + timedelta(days=phase["duration_days"])
        phases.append({
            "name": phase["name"],
            "start_date": current_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "duration_days": phase["duration_days"],
            "content_focus": phase["content_focus"],
        })
        current_date = end_date

    activity = Activity(
        id=str(uuid.uuid4()),
        user_id="system",
        type="campaign_created",
        description=f"Campaign created: {name}",
        meta={"campaign_id": campaign_id, "name": name, "type": campaign_type},
    )
    db.add(activity)
    await db.flush()

    return {
        "campaign_id": campaign_id,
        "name": name,
        "type": campaign_type,
        "platforms": platforms or template["platforms"],
        "start_date": start.strftime("%Y-%m-%d"),
        "end_date": current_date.strftime("%Y-%m-%d"),
        "total_days": total_days,
        "phases": phases,
        "goals": goals or {},
    }


def get_campaign_types() -> list[dict[str, Any]]:
    """Get available campaign type templates."""
    return [
        {"key": k, "name": v["name"], "phases": len(v["phases"]), "total_days": sum(p["duration_days"] for p in v["phases"])}
        for k, v in CAMPAIGN_TYPES.items()
    ]
