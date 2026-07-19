"""Content Pillar Manager — define themes, set mix %, track performance per pillar.

Organizes content strategy around 3-5 core pillars with
performance tracking and mix recommendations.
"""
import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post, AnalyticsMetric

logger = logging.getLogger(__name__)

# Default pillar templates
DEFAULT_PILLARS = [
    {
        "id": "pillar-educational",
        "name": "Educational",
        "description": "Teach your audience something valuable",
        "color": "#3b82f6",
        "target_percentage": 30,
        "content_types": ["how-to", "tutorial", "tips", "guide", "explanation"],
        "examples": ["5 tips for...", "How to...", "Beginner's guide to...", "What is..."],
    },
    {
        "id": "pillar-engagement",
        "name": "Engagement",
        "description": "Spark conversations and community interaction",
        "color": "#8b5cf6",
        "target_percentage": 25,
        "content_types": ["question", "poll", "debate", "opinion", "story"],
        "examples": ["What do you think about...", "Hot take:...", "Poll: A or B?"],
    },
    {
        "id": "pillar-promotional",
        "name": "Promotional",
        "description": "Showcase your product, features, and wins",
        "color": "#22c55e",
        "target_percentage": 15,
        "content_types": ["product-update", "feature", "case-study", "testimonial", "announcement"],
        "examples": ["Introducing...", "How [client] achieved...", "New feature:"],
    },
    {
        "id": "pillar-behind-scenes",
        "name": "Behind the Scenes",
        "description": "Show the human side of your brand",
        "color": "#f59e0b",
        "target_percentage": 15,
        "content_types": ["team", "process", "culture", "milestone", "day-in-life"],
        "examples": ["Meet the team...", "How we built...", "A day at..."],
    },
    {
        "id": "pillar-curated",
        "name": "Curated / Industry",
        "description": "Share industry news and curated content",
        "color": "#06b6d4",
        "target_percentage": 15,
        "content_types": ["news", "trend", "roundup", "resource", "bookmark"],
        "examples": ["Top 5 reads this week...", "Industry trend:", "Resource of the week:"],
    },
]


async def get_pillars(
    db: AsyncSession,
    workspace_id: str,
) -> dict[str, Any]:
    """Get content pillars with performance data."""
    # Get all posts and their analytics
    result = await db.execute(
        select(
            Post.meta,
            func.sum(AnalyticsMetric.engagement).label("engagement"),
            func.sum(AnalyticsMetric.impressions).label("impressions"),
            func.count(Post.id).label("post_count"),
        )
        .join(AnalyticsMetric, Post.id == AnalyticsMetric.post_id)
        .where(Post.workspace_id == workspace_id, Post.status == "published")
        .group_by(Post.meta)
    )
    rows = result.all()

    # Calculate performance per pillar
    pillar_stats: dict[str, dict] = {}
    for meta, engagement, impressions, post_count in rows:
        meta_data = meta or {}
        pillar = meta_data.get("content_pillar", "uncategorized")
        if pillar not in pillar_stats:
            pillar_stats[pillar] = {"engagement": 0, "impressions": 0, "posts": 0}
        pillar_stats[pillar]["engagement"] += engagement or 0
        pillar_stats[pillar]["impressions"] += impressions or 0
        pillar_stats[pillar]["posts"] += post_count or 0

    # Merge with default pillars
    pillars = []
    for default in DEFAULT_PILLARS:
        stats = pillar_stats.get(default["id"], pillar_stats.get(default["name"].lower(), {}))
        total_posts = stats.get("posts", 0)
        total_eng = stats.get("engagement", 0)
        total_imp = stats.get("impressions", 0)
        eng_rate = (total_eng / total_imp * 100) if total_imp > 0 else 0

        # Actual percentage of content
        all_posts = sum(s["posts"] for s in pillar_stats.values()) or 1
        actual_pct = round(total_posts / all_posts * 100) if all_posts > 0 else 0

        pillars.append({
            **default,
            "actual_percentage": actual_pct,
            "total_posts": total_posts,
            "avg_engagement_rate": round(eng_rate, 2),
            "total_engagement": total_eng,
            "performance_score": round(min(eng_rate * 10, 100), 1),
        })

    # Add uncategorized
    uncategorized = pillar_stats.get("uncategorized", pillar_stats.get("unknown", {}))
    if uncategorized.get("posts", 0) > 0:
        pillars.append({
            "id": "pillar-uncategorized",
            "name": "Uncategorized",
            "description": "Posts without a content pillar assigned",
            "color": "#6b7280",
            "target_percentage": 0,
            "actual_percentage": round(uncategorized["posts"] / max(sum(s["posts"] for s in pillar_stats.values()), 1) * 100),
            "total_posts": uncategorized["posts"],
            "avg_engagement_rate": round(
                (uncategorized.get("engagement", 0) / max(uncategorized.get("impressions", 1), 1) * 100), 2
            ),
            "total_engagement": uncategorized.get("engagement", 0),
            "performance_score": 0,
        })

    # Recommendations
    recommendations: list[str] = []
    for p in pillars:
        if p.get("actual_percentage", 0) > p.get("target_percentage", 0) + 10:
            recommendations.append(
                f"Reduce {p['name']} content from {p['actual_percentage']}% to ~{p['target_percentage']}% target"
            )
        elif p.get("actual_percentage", 0) < p.get("target_percentage", 0) - 10:
            recommendations.append(
                f"Increase {p['name']} content from {p['actual_percentage']}% to ~{p['target_percentage']}% target"
            )

    return {
        "pillars": pillars,
        "total_posts": sum(p["total_posts"] for p in pillars),
        "recommendations": recommendations,
    }


async def set_post_pillar(
    db: AsyncSession,
    post_id: str,
    pillar_id: str,
) -> dict[str, Any]:
    """Assign a content pillar to a post."""
    from app.models.post_platform import PostPlatform

    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_none()
    if not post:
        return {"error": f"Post {post_id} not found"}

    meta = post.meta or {}
    meta["content_pillar"] = pillar_id
    post.meta = meta

    await db.flush()
    return {"post_id": post_id, "pillar": pillar_id}


def get_pillar_templates() -> list[dict[str, Any]]:
    """Get default pillar templates."""
    return DEFAULT_PILLARS
