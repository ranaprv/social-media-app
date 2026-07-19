"""Content calendar analytics — what posted when + performance.

Provides analytics about posting patterns, content distribution,
and scheduling efficiency.
"""
import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post, AnalyticsMetric
from app.models.post_platform import PostPlatform

logger = logging.getLogger(__name__)


async def get_calendar_analytics(
    db: AsyncSession,
    workspace_id: str,
    days: int = 90,
) -> dict[str, Any]:
    """Get analytics about posting patterns and performance."""
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Posts by day of week
    dow_result = await db.execute(
        select(
            func.extract("dow", PostPlatform.scheduled_at),
            func.count(PostPlatform.id),
        )
        .where(
            PostPlatform.workspace_id == workspace_id,
            PostPlatform.scheduled_at >= cutoff,
        )
        .group_by(func.extract("dow", PostPlatform.scheduled_at))
    )
    posts_by_dow = {int(row[0]): row[1] for row in dow_result.all()}

    # Posts by hour
    hour_result = await db.execute(
        select(
            func.extract("hour", PostPlatform.scheduled_at),
            func.count(PostPlatform.id),
        )
        .where(
            PostPlatform.workspace_id == workspace_id,
            PostPlatform.scheduled_at >= cutoff,
        )
        .group_by(func.extract("hour", PostPlatform.scheduled_at))
    )
    posts_by_hour = {int(row[0]): row[1] for row in hour_result.all()}

    # Posts by platform
    platform_result = await db.execute(
        select(PostPlatform.platform, func.count(PostPlatform.id))
        .where(
            PostPlatform.workspace_id == workspace_id,
            PostPlatform.scheduled_at >= cutoff,
        )
        .group_by(PostPlatform.platform)
    )
    posts_by_platform = {row[0]: row[1] for row in platform_result.all()}

    # Posts by status
    status_result = await db.execute(
        select(PostPlatform.status, func.count(PostPlatform.id))
        .where(
            PostPlatform.workspace_id == workspace_id,
            PostPlatform.created_at >= cutoff,
        )
        .group_by(PostPlatform.status)
    )
    posts_by_status = {row[0]: row[1] for row in status_result.all()}

    # Average time between schedule and publish
    delay_result = await db.execute(
        select(
            func.avg(
                func.extract("epoch", PostPlatform.published_at) - func.extract("epoch", PostPlatform.scheduled_at)
            )
        ).where(
            PostPlatform.workspace_id == workspace_id,
            PostPlatform.status == "published",
            PostPlatform.scheduled_at.isnot(None),
            PostPlatform.published_at.isnot(None),
        )
    )
    avg_delay_seconds = delay_result.scalar() or 0

    # Publishing consistency (posts per week)
    total_posts = sum(posts_by_dow.values())
    weeks = max(days / 7, 1)
    posts_per_week = round(total_posts / weeks, 1)

    # Best performing content patterns
    perf_result = await db.execute(
        select(
            Post.content,
            AnalyticsMetric.engagement,
            AnalyticsMetric.impressions,
        )
        .join(AnalyticsMetric, Post.id == AnalyticsMetric.post_id)
        .where(
            Post.workspace_id == workspace_id,
            Post.published_at >= cutoff,
        )
        .limit(100)
    )
    perf_rows = perf_result.all()

    # Analyze content patterns
    pattern_scores: dict[str, list[float]] = {
        "short (<100 chars)": [],
        "medium (100-300 chars)": [],
        "long (300+ chars)": [],
        "with_emoji": [],
        "without_emoji": [],
        "with_question": [],
        "without_question": [],
    }

    for content, engagement, impressions in perf_rows:
        eng_rate = (engagement / impressions * 100) if impressions and impressions > 0 else 0
        content_len = len(content or "")

        if content_len < 100:
            pattern_scores["short (<100 chars)"].append(eng_rate)
        elif content_len < 300:
            pattern_scores["medium (100-300 chars)"].append(eng_rate)
        else:
            pattern_scores["long (300+ chars)"].append(eng_rate)

        if any(ord(c) > 0x1F600 for c in (content or "")):
            pattern_scores["with_emoji"].append(eng_rate)
        else:
            pattern_scores["without_emoji"].append(eng_rate)

        if "?" in (content or ""):
            pattern_scores["with_question"].append(eng_rate)
        else:
            pattern_scores["without_question"].append(eng_rate)

    pattern_avgs = {
        k: round(sum(v) / len(v), 2) if v else 0
        for k, v in pattern_scores.items()
    }

    return {
        "period_days": days,
        "posting_patterns": {
            "by_day_of_week": posts_by_dow,
            "by_hour": posts_by_hour,
            "by_platform": posts_by_platform,
            "by_status": posts_by_status,
        },
        "consistency": {
            "total_posts": total_posts,
            "posts_per_week": posts_per_week,
            "avg_publish_delay_seconds": round(avg_delay_seconds, 0),
        },
        "content_performance": pattern_avgs,
    }
