"""Data-driven best-time recommender.

Analyzes AnalyticsMetric records to find when posts get the most
engagement per platform, then recommends scheduling times.

Replaces static best_times with real performance data.
"""
import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post, AnalyticsMetric
from app.models.post_platform import PostPlatform

logger = logging.getLogger(__name__)

# Fallback static data when no analytics exist yet
STATIC_BEST_TIMES: dict[str, list[dict[str, Any]]] = {
    "linkedin": [
        {"day": 1, "hour": 8, "score": 0.95, "label": "Tuesday 8 AM"},
        {"day": 2, "hour": 10, "score": 0.92, "label": "Wednesday 10 AM"},
        {"day": 3, "hour": 9, "score": 0.88, "label": "Thursday 9 AM"},
        {"day": 1, "hour": 12, "score": 0.85, "label": "Tuesday 12 PM"},
        {"day": 4, "hour": 8, "score": 0.82, "label": "Friday 8 AM"},
    ],
    "x": [
        {"day": 1, "hour": 12, "score": 0.93, "label": "Tuesday 12 PM"},
        {"day": 2, "hour": 9, "score": 0.90, "label": "Wednesday 9 AM"},
        {"day": 3, "hour": 17, "score": 0.87, "label": "Thursday 5 PM"},
        {"day": 0, "hour": 10, "score": 0.84, "label": "Monday 10 AM"},
        {"day": 4, "hour": 14, "score": 0.80, "label": "Friday 2 PM"},
    ],
    "instagram": [
        {"day": 1, "hour": 11, "score": 0.94, "label": "Tuesday 11 AM"},
        {"day": 3, "hour": 14, "score": 0.91, "label": "Thursday 2 PM"},
        {"day": 5, "hour": 11, "score": 0.89, "label": "Saturday 11 AM"},
        {"day": 2, "hour": 19, "score": 0.86, "label": "Wednesday 7 PM"},
        {"day": 0, "hour": 20, "score": 0.83, "label": "Monday 8 PM"},
    ],
    "facebook": [
        {"day": 1, "hour": 13, "score": 0.92, "label": "Tuesday 1 PM"},
        {"day": 3, "hour": 15, "score": 0.89, "label": "Thursday 3 PM"},
        {"day": 2, "hour": 11, "score": 0.86, "label": "Wednesday 11 AM"},
        {"day": 4, "hour": 10, "score": 0.83, "label": "Friday 10 AM"},
        {"day": 0, "hour": 12, "score": 0.80, "label": "Monday 12 PM"},
    ],
    "youtube": [
        {"day": 5, "hour": 15, "score": 0.96, "label": "Saturday 3 PM"},
        {"day": 6, "hour": 9, "score": 0.93, "label": "Sunday 9 AM"},
        {"day": 3, "hour": 14, "score": 0.88, "label": "Thursday 2 PM"},
        {"day": 1, "hour": 16, "score": 0.85, "label": "Tuesday 4 PM"},
        {"day": 4, "hour": 17, "score": 0.82, "label": "Friday 5 PM"},
    ],
}

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


async def get_best_times_for_workspace(
    db: AsyncSession,
    workspace_id: str,
    platform: str | None = None,
    min_data_points: int = 10,
) -> dict[str, Any]:
    """Analyze actual post performance to recommend best scheduling times.

    Queries published posts with their analytics, groups by day-of-week + hour,
    and ranks by average engagement rate.

    Returns:
    {
        "source": "analytics" | "static",
        "data_points": int,
        "platforms": {
            "linkedin": [
                {"day": 1, "hour": 8, "score": 0.95, "label": "Tuesday 8 AM",
                 "avg_engagement": 142.5, "post_count": 12}
            ]
        },
        "heatmap": [...]
    }
    """
    platforms_to_analyze = [platform] if platform else ["linkedin", "x", "instagram", "facebook", "youtube"]
    result_platforms: dict[str, list[dict[str, Any]]] = {}
    total_data_points = 0

    for p in platforms_to_analyze:
        # Get published posts with analytics for this workspace+platform
        query = (
            select(
                Post.id,
                Post.published_at,
                AnalyticsMetric.engagement,
                AnalyticsMetric.impressions,
                AnalyticsMetric.reach,
                AnalyticsMetric.clicks,
            )
            .join(AnalyticsMetric, Post.id == AnalyticsMetric.post_id)
            .where(
                Post.workspace_id == workspace_id,
                AnalyticsMetric.platform == p,
                Post.published_at.isnot(None),
                Post.status == "published",
            )
            .order_by(Post.published_at.desc())
            .limit(500)  # Last 500 posts for analysis
        )

        rows = (await db.execute(query)).all()

        if len(rows) < min_data_points:
            # Not enough data — use static fallback
            result_platforms[p] = STATIC_BEST_TIMES.get(p, [])
            continue

        total_data_points += len(rows)

        # Group by (day_of_week, hour)
        slot_data: dict[tuple[int, int], list[dict]] = {}
        for post_id, published_at, engagement, impressions, reach, clicks in rows:
            if not published_at:
                continue
            day = published_at.weekday()  # 0=Monday
            hour = published_at.hour
            key = (day, hour)

            eng_rate = (engagement / impressions * 100) if impressions and impressions > 0 else 0

            if key not in slot_data:
                slot_data[key] = []
            slot_data[key].append({
                "engagement": engagement or 0,
                "impressions": impressions or 0,
                "engagement_rate": eng_rate,
                "reach": reach or 0,
                "clicks": clicks or 0,
            })

        # Calculate average engagement rate per slot
        slot_scores: list[dict[str, Any]] = []
        for (day, hour), posts in slot_data.items():
            if len(posts) < 2:  # Need at least 2 data points
                continue
            avg_eng_rate = sum(p["engagement_rate"] for p in posts) / len(posts)
            avg_engagement = sum(p["engagement"] for p in posts) / len(posts)
            avg_impressions = sum(p["impressions"] for p in posts) / len(posts)
            total_clicks = sum(p["clicks"] for p in posts)

            slot_scores.append({
                "day": day,
                "hour": hour,
                "score": min(avg_eng_rate / 10, 1.0),  # Normalize to 0-1
                "label": f"{DAY_NAMES[day]} {hour}:00",
                "avg_engagement": round(avg_engagement, 1),
                "avg_impressions": round(avg_impressions, 1),
                "post_count": len(posts),
                "total_clicks": total_clicks,
            })

        # Sort by score descending, take top 7
        slot_scores.sort(key=lambda x: x["score"], reverse=True)
        result_platforms[p] = slot_scores[:7]

    # Generate heatmap (all slots with scores)
    heatmap: list[dict[str, Any]] = []
    for p, slots in result_platforms.items():
        for slot in slots:
            heatmap.append({
                "day": DAY_NAMES[slot["day"]][:3],
                "hour": slot["hour"],
                "score": slot["score"],
                "platform": p,
            })

    source = "analytics" if total_data_points >= min_data_points else "static"

    return {
        "source": source,
        "data_points": total_data_points,
        "platforms": result_platforms,
        "heatmap": heatmap,
    }


async def get_next_suggested_time(
    db: AsyncSession,
    workspace_id: str,
    platform: str,
) -> dict[str, Any] | None:
    """Get the next optimal time slot to schedule a post for a platform.

    Looks at the next 7 days and picks the highest-scoring slot
    that hasn't already been taken.
    """
    best_times = await get_best_times_for_workspace(db, workspace_id, platform)
    platform_times = best_times.get("platforms", {}).get(platform, [])

    if not platform_times:
        return None

    # Find already-scheduled posts for this platform in the next 7 days
    now = datetime.utcnow()
    week_later = now + timedelta(days=7)

    from app.models.post_platform import PostPlatform as PP
    scheduled = await db.execute(
        select(PP.scheduled_at).where(
            PP.workspace_id == workspace_id,
            PP.platform == platform,
            PP.status.in_(["scheduled", "publishing"]),
            PP.scheduled_at >= now,
            PP.scheduled_at <= week_later,
        )
    )
    taken_slots = set()
    for (sa,) in scheduled.all():
        if sa:
            taken_slots.add((sa.weekday(), sa.hour))

    # Find first available slot in the next 7 days
    for slot in platform_times:
        day, hour = slot["day"], slot["hour"]
        # Check each of the next 7 days for this day-of-week + hour
        for days_ahead in range(7):
            candidate = now + timedelta(days=days_ahead)
            if candidate.weekday() == day and candidate.hour == hour:
                # Check if slot is taken
                if (day, hour) not in taken_slots:
                    # Set time to the recommended hour
                    suggested = candidate.replace(hour=hour, minute=0, second=0, microsecond=0)
                    if suggested > now:
                        return {
                            "platform": platform,
                            "suggested_at": suggested.isoformat(),
                            "score": slot["score"],
                            "label": slot["label"],
                            "avg_engagement": slot.get("avg_engagement", 0),
                            "reason": f"Based on {slot.get('post_count', 0)} prior posts with avg engagement rate {slot['score']*100:.1f}%",
                        }
                break

    # Fallback: return the top slot
    top = platform_times[0]
    return {
        "platform": platform,
        "suggested_at": (now + timedelta(days=1)).replace(hour=top["hour"], minute=0).isoformat(),
        "score": top["score"],
        "label": top["label"],
        "avg_engagement": top.get("avg_engagement", 0),
        "reason": f"Top performing time slot for {platform}",
    }
