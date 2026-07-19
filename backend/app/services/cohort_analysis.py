"""Advanced analytics — cohort analysis for audience insights.

Groups posts into cohorts based on characteristics and compares
performance across cohorts.
"""
import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post, AnalyticsMetric

logger = logging.getLogger(__name__)


async def cohort_analysis(
    db: AsyncSession,
    workspace_id: str,
    cohort_by: str = "platform",
    days: int = 90,
) -> dict[str, Any]:
    """Perform cohort analysis on published posts.

    Cohort options:
      - platform: Group by platform
      - content_type: Group by post type (text, image, video)
      - time_of_day: Group by posting time (morning, afternoon, evening)
      - day_of_week: Group by day of week
    """
    cutoff = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(
            Post.id,
            Post.platform,
            Post.content,
            Post.published_at,
            Post.media_urls,
            AnalyticsMetric.impressions,
            AnalyticsMetric.engagement,
            AnalyticsMetric.reach,
            AnalyticsMetric.clicks,
            AnalyticsMetric.likes,
            AnalyticsMetric.shares,
            AnalyticsMetric.comments,
        )
        .join(AnalyticsMetric, Post.id == AnalyticsMetric.post_id)
        .where(
            Post.workspace_id == workspace_id,
            Post.status == "published",
            Post.published_at >= cutoff,
        )
    )
    rows = result.all()

    if not rows:
        return {"cohorts": [], "message": "No data available for analysis"}

    # Assign each post to a cohort
    cohorts: dict[str, list[dict]] = {}

    for row in rows:
        post_id, platform, content, published_at, media_urls, impressions, engagement, reach, clicks, likes, shares, comments = row

        # Determine cohort
        if cohort_by == "platform":
            cohort_key = platform
        elif cohort_by == "content_type":
            content_len = len(content or "")
            if media_urls:
                has_video = any("video" in str(u).lower() for u in (media_urls or []))
                cohort_key = "video" if has_video else "image"
            elif content_len < 100:
                cohort_key = "short_text"
            elif content_len < 300:
                cohort_key = "medium_text"
            else:
                cohort_key = "long_text"
        elif cohort_by == "time_of_day":
            hour = published_at.hour if published_at else 12
            if 6 <= hour < 12:
                cohort_key = "morning"
            elif 12 <= hour < 17:
                cohort_key = "afternoon"
            elif 17 <= hour < 21:
                cohort_key = "evening"
            else:
                cohort_key = "night"
        elif cohort_by == "day_of_week":
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            cohort_key = day_names[published_at.weekday()] if published_at else "Unknown"
        else:
            cohort_key = "all"

        if cohort_key not in cohorts:
            cohorts[cohort_key] = []

        imp = impressions or 0
        eng = engagement or 0
        cohorts[cohort_key].append({
            "impressions": imp,
            "engagement": eng,
            "reach": reach or 0,
            "clicks": clicks or 0,
            "likes": likes or 0,
            "shares": shares or 0,
            "comments": comments or 0,
            "engagement_rate": (eng / imp * 100) if imp > 0 else 0,
        })

    # Calculate cohort summaries
    summaries: list[dict[str, Any]] = []
    for cohort_key, posts in cohorts.items():
        n = len(posts)
        total_imp = sum(p["impressions"] for p in posts)
        total_eng = sum(p["engagement"] for p in posts)
        total_reach = sum(p["reach"] for p in posts)
        total_clicks = sum(p["clicks"] for p in posts)
        avg_eng_rate = sum(p["engagement_rate"] for p in posts) / n

        summaries.append({
            "cohort": cohort_key,
            "post_count": n,
            "avg_impressions": round(total_imp / n),
            "avg_engagement": round(total_eng / n),
            "avg_engagement_rate": round(avg_eng_rate, 2),
            "total_reach": total_reach,
            "total_clicks": total_clicks,
            "avg_reach": round(total_reach / n),
        })

    # Sort by engagement rate
    summaries.sort(key=lambda x: x["avg_engagement_rate"], reverse=True)

    # Find best and worst cohorts
    if summaries:
        best = summaries[0]
        worst = summaries[-1]
        insight = f"{best['cohort']} outperforms {worst['cohort']} by {best['avg_engagement_rate'] - worst['avg_engagement_rate']:.1f}% engagement rate"
    else:
        insight = "Insufficient data"

    return {
        "cohort_by": cohort_by,
        "period_days": days,
        "total_posts": len(rows),
        "cohorts": summaries,
        "best_cohort": summaries[0] if summaries else None,
        "worst_cohort": summaries[-1] if summaries else None,
        "insight": insight,
    }
