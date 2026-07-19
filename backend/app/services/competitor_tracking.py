"""Competitor tracking — monitor competitor posting patterns.

Tracks competitor accounts and analyzes their posting patterns,
content types, and engagement metrics.
"""
import logging
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Predefined competitor tracking templates
COMPETITOR_TEMPLATES = {
    "linkedin": {
        "tracks": ["company_page", "employee_posts", "sponsored_content"],
        "metrics": ["post_frequency", "avg_engagement", "content_types", "hashtag_usage"],
    },
    "x": {
        "tracks": ["tweets", "threads", "retweets", "replies"],
        "metrics": ["post_frequency", "engagement_rate", "top_topics", "hashtag_trends"],
    },
    "instagram": {
        "tracks": ["posts", "reels", "stories", "carousels"],
        "metrics": ["post_frequency", "engagement_rate", "hashtag_mix", "content_format"],
    },
    "facebook": {
        "tracks": ["page_posts", "group_activity", "ads"],
        "metrics": ["post_frequency", "engagement_rate", "reach", "content_types"],
    },
    "youtube": {
        "tracks": ["videos", "shorts", "community_posts"],
        "metrics": ["upload_frequency", "avg_views", "avg_watch_time", "thumbnail_style"],
    },
}


async def add_competitor(
    db: AsyncSession,
    workspace_id: str,
    competitor_name: str,
    platforms: list[str],
    profile_urls: dict[str, str] | None = None,
    notes: str = "",
) -> dict[str, Any]:
    """Add a competitor to track."""
    from app.models.content import Activity
    import uuid

    activity = Activity(
        id=str(uuid.uuid4()),
        user_id="system",
        type="competitor_added",
        description=f"Added competitor: {competitor_name}",
        meta={
            "competitor_name": competitor_name,
            "platforms": platforms,
            "profile_urls": profile_urls or {},
            "notes": notes,
        },
    )
    db.add(activity)
    await db.flush()

    return {
        "competitor_name": competitor_name,
        "platforms": platforms,
        "tracking_since": datetime.utcnow().isoformat(),
    }


async def analyze_competitor_patterns(
    competitor_name: str,
    platform: str,
    posts: list[dict[str, Any]],
) -> dict[str, Any]:
    """Analyze a competitor's posting patterns from their data."""
    if not posts:
        return {
            "competitor": competitor_name,
            "platform": platform,
            "message": "No data available for analysis",
        }

    # Analyze patterns
    total_posts = len(posts)
    avg_length = sum(len(p.get("content", "")) for p in posts) / total_posts
    has_media = sum(1 for p in posts if p.get("has_media")) / total_posts * 100
    has_hashtags = sum(1 for p in posts if p.get("hashtags")) / total_posts * 100
    has_cta = sum(1 for p in posts if p.get("has_cta")) / total_posts * 100

    # Posting frequency
    if total_posts > 1:
        dates = sorted([p.get("date", "") for p in posts if p.get("date")])
        if dates:
            from datetime import datetime as dt
            try:
                first = dt.fromisoformat(dates[0])
                last = dt.fromisoformat(dates[-1])
                days = (last - first).days or 1
                frequency = total_posts / days
            except ValueError:
                frequency = 0
        else:
            frequency = 0
    else:
        frequency = 0

    # Content type distribution
    content_types: dict[str, int] = {}
    for p in posts:
        ct = p.get("content_type", "text")
        content_types[ct] = content_types.get(ct, 0) + 1

    return {
        "competitor": competitor_name,
        "platform": platform,
        "total_posts_analyzed": total_posts,
        "avg_content_length": round(avg_length),
        "media_usage_pct": round(has_media, 1),
        "hashtag_usage_pct": round(has_hashtags, 1),
        "cta_usage_pct": round(has_cta, 1),
        "posting_frequency_per_day": round(frequency, 2),
        "content_types": content_types,
        "insights": [
            f"Posts {round(frequency * 7, 1)} times per week",
            f"Uses media in {round(has_media)}% of posts",
            f"Average content length: {round(avg_length)} chars",
        ],
    }


def get_tracking_templates(platform: str) -> dict[str, Any]:
    """Get tracking templates for a platform."""
    return COMPETITOR_TEMPLATES.get(platform, {})
