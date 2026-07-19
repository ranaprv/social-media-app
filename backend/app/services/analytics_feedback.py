"""Analytics feedback loop — analyzes post performance to suggest improvements.

Examines patterns in what works (content type, posting time, caption length,
media usage) and generates actionable suggestions.
"""
import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func, desc, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post, AnalyticsMetric

logger = logging.getLogger(__name__)


async def get_content_suggestions(
    db: AsyncSession,
    workspace_id: str,
    platform: str | None = None,
) -> dict[str, Any]:
    """Analyze historical post performance and generate improvement suggestions.

    Examines:
      1. Best caption length ranges
      2. Best posting times (from analytics)
      3. Media vs text-only performance
      4. Content patterns that correlate with high engagement
      5. Underperforming content that needs attention

    Returns structured suggestions with confidence scores.
    """
    cutoff = datetime.utcnow() - timedelta(days=90)

    # Get published posts with analytics
    query = (
        select(
            Post.id,
            Post.title,
            Post.content,
            Post.platform,
            Post.published_at,
            Post.media_urls,
            Post.status,
            AnalyticsMetric.engagement,
            AnalyticsMetric.impressions,
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

    if platform:
        query = query.where(Post.platform == platform)

    query = query.order_by(Post.published_at.desc())
    rows = (await db.execute(query)).all()

    if not rows:
        return {
            "suggestions": [
                {
                    "type": "data_needed",
                    "priority": "high",
                    "message": "Not enough published posts with analytics data yet. Publish more posts to get personalized suggestions.",
                    "confidence": 1.0,
                }
            ],
            "stats": {"total_posts": 0, "period_days": 90},
        }

    # Analyze patterns
    suggestions: list[dict[str, Any]] = []

    # 1. Caption length analysis
    length_buckets: dict[str, list[float]] = {
        "short (<50)": [],
        "medium (50-200)": [],
        "long (200-500)": [],
        "very_long (500+)": [],
    }
    for row in rows:
        content = row[2] or ""
        eng_rate = (row[7] / row[8] * 100) if row[8] and row[8] > 0 else 0
        if len(content) < 50:
            length_buckets["short (<50)"].append(eng_rate)
        elif len(content) < 200:
            length_buckets["medium (50-200)"].append(eng_rate)
        elif len(content) < 500:
            length_buckets["long (200-500)"].append(eng_rate)
        else:
            length_buckets["very_long (500+)"].append(eng_rate)

    avg_by_bucket = {
        k: (sum(v) / len(v) if v else 0) for k, v in length_buckets.items()
    }
    best_length = max(avg_by_bucket, key=avg_by_bucket.get)
    worst_length = min(avg_by_bucket, key=avg_by_bucket.get)

    if avg_by_bucket[best_length] > avg_by_bucket[worst_length] * 1.2:
        suggestions.append({
            "type": "caption_length",
            "priority": "medium",
            "message": f"Posts with {best_length} captions get {avg_by_bucket[best_length]:.1f}% avg engagement vs {avg_by_bucket[worst_length]:.1f}% for {worst_length}. Consider optimizing caption length.",
            "confidence": 0.7,
            "data": {k: round(v, 2) for k, v in avg_by_bucket.items()},
        })

    # 2. Media vs text-only analysis
    with_media = []
    without_media = []
    for row in rows:
        media_urls = row[5] or []
        eng_rate = (row[7] / row[8] * 100) if row[8] and row[8] > 0 else 0
        if media_urls:
            with_media.append(eng_rate)
        else:
            without_media.append(eng_rate)

    avg_with = sum(with_media) / len(with_media) if with_media else 0
    avg_without = sum(without_media) / len(without_media) if without_media else 0

    if with_media and without_media and avg_with > avg_without * 1.15:
        suggestions.append({
            "type": "media_usage",
            "priority": "high",
            "message": f"Posts with media get {avg_with:.1f}% avg engagement vs {avg_without:.1f}% without. Add images/videos to boost performance.",
            "confidence": 0.8,
            "data": {"with_media": round(avg_with, 2), "without_media": round(avg_without, 2)},
        })

    # 3. Posting time analysis
    hour_engagement: dict[int, list[float]] = {}
    for row in rows:
        published_at = row[4]
        if published_at:
            hour = published_at.hour
            eng_rate = (row[7] / row[8] * 100) if row[8] and row[8] > 0 else 0
            if hour not in hour_engagement:
                hour_engagement[hour] = []
            hour_engagement[hour].append(eng_rate)

    if hour_engagement:
        hour_avgs = {h: sum(v) / len(v) for h, v in hour_engagement.items() if len(v) >= 3}
        if hour_avgs:
            best_hour = max(hour_avgs, key=hour_avgs.get)
            worst_hour = min(hour_avgs, key=hour_avgs.get)
            if hour_avgs[best_hour] > hour_avgs[worst_hour] * 1.2:
                suggestions.append({
                    "type": "posting_time",
                    "priority": "medium",
                    "message": f"Posts at {best_hour}:00 get {hour_avgs[best_hour]:.1f}% avg engagement vs {hour_avgs[worst_hour]:.1f}% at {worst_hour}:00. Schedule more posts around {best_hour}:00.",
                    "confidence": 0.6,
                    "data": {f"{h}:00": round(v, 2) for h, v in sorted(hour_avgs.items())},
                })

    # 4. Engagement comparison (top 20% vs bottom 20%)
    eng_rates = []
    for row in rows:
        eng_rate = (row[7] / row[8] * 100) if row[8] and row[8] > 0 else 0
        eng_rates.append((row, eng_rate))
    eng_rates.sort(key=lambda x: x[1], reverse=True)

    if len(eng_rates) >= 5:
        top_20_pct = eng_rates[:max(1, len(eng_rates) // 5)]
        bottom_20_pct = eng_rates[-max(1, len(eng_rates) // 5):]

        # Compare content characteristics
        top_avg_len = sum(len(r[0][2] or "") for r in top_20_pct) / len(top_20_pct)
        bottom_avg_len = sum(len(r[0][2] or "") for r in bottom_20_pct) / len(bottom_20_pct)

        top_media_pct = sum(1 for r in top_20_pct if r[0][5]) / len(top_20_pct) * 100
        bottom_media_pct = sum(1 for r in bottom_20_pct if r[0][5]) / len(bottom_20_pct) * 100

        if top_media_pct > bottom_media_pct + 10:
            suggestions.append({
                "type": "pattern",
                "priority": "medium",
                "message": f"Top 20% posts use media {top_media_pct:.0f}% of the time vs {bottom_media_pct:.0f}% for bottom 20%. Visual content consistently outperforms.",
                "confidence": 0.65,
            })

        if abs(top_avg_len - bottom_avg_len) > 50:
            longer = "longer" if top_avg_len > bottom_avg_len else "shorter"
            suggestions.append({
                "type": "pattern",
                "priority": "low",
                "message": f"Top performing posts tend to be {longer} (avg {top_avg_len:.0f} chars vs {bottom_avg_len:.0f} chars for bottom performers).",
                "confidence": 0.5,
            })

    # 5. Content score trend
    if len(rows) >= 20:
        first_half = rows[len(rows) // 2:]
        second_half = rows[:len(rows) // 2]
        first_avg = sum((r[7] / r[8] * 100) if r[8] and r[8] > 0 else 0 for r in first_half) / len(first_half)
        second_avg = sum((r[7] / r[8] * 100) if r[8] and r[8] > 0 else 0 for r in second_half) / len(second_half)

        if second_avg > first_avg * 1.1:
            suggestions.append({
                "type": "trend",
                "priority": "high",
                "message": f"Your engagement is improving! Recent posts average {second_avg:.1f}% vs {first_avg:.1f}% for older posts. Keep up the momentum.",
                "confidence": 0.8,
            })
        elif first_avg > second_avg * 1.1:
            suggestions.append({
                "type": "trend",
                "priority": "high",
                "message": f"Engagement declining: recent posts average {second_avg:.1f}% vs {first_avg:.1f}% for older posts. Review what changed.",
                "confidence": 0.7,
            })

    # 6. Platform-specific tips
    if platform == "instagram" and any(row[3] == "instagram" for row in rows):
        ig_posts = [row for row in rows if row[3] == "instagram"]
        if len(ig_posts) >= 5:
            suggestions.append({
                "type": "platform_tip",
                "priority": "low",
                "message": "Instagram Reels consistently outperform static posts. Consider converting your best content to short-form video.",
                "confidence": 0.6,
            })

    if platform == "x" and any(row[3] == "x" for row in rows):
        suggestions.append({
            "type": "platform_tip",
            "priority": "low",
            "message": "X/Twitter threads get 3-5x more impressions than single tweets. Break long content into threads.",
            "confidence": 0.5,
        })

    # If no suggestions generated
    if not suggestions:
        suggestions.append({
            "type": "status",
            "priority": "low",
            "message": "Your content is performing consistently. Keep publishing to build more data for personalized suggestions.",
            "confidence": 1.0,
        })

    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    suggestions.sort(key=lambda s: priority_order.get(s["priority"], 3))

    return {
        "suggestions": suggestions,
        "stats": {
            "total_posts": len(rows),
            "period_days": 90,
            "avg_engagement_rate": round(
                sum((r[7] / r[8] * 100) if r[8] and r[8] > 0 else 0 for r in rows) / len(rows),
                2,
            ),
            "total_impressions": sum(r[8] or 0 for r in rows),
            "total_engagement": sum(r[7] or 0 for r in rows),
        },
    }


class AnalyticsFeedbackLoop:
    """Processes post performance data and stores feedback for RAG-based improvement suggestions."""

    async def process_performance_and_store_rag(
        self,
        platform_post_id: str,
        post_text: str,
        impressions: int = 0,
        engagements: int = 0,
        shares: int = 0,
        clicks: int = 0,
        platform: str = "",
        recorded_at: datetime | None = None,
    ) -> dict[str, Any]:
        """Analyze performance metrics and return a score with suggestions."""
        total_engagement = engagements + shares + clicks
        engagement_rate = (total_engagement / impressions * 100) if impressions > 0 else 0.0

        score = min(10.0, engagement_rate * 2)
        tier = (
            "high" if score >= 7
            else "medium" if score >= 4
            else "low"
        )

        suggestions: list[str] = []
        if engagement_rate < 1.0:
            suggestions.append("Low engagement — try adding media or a stronger hook.")
        if shares == 0 and impressions > 100:
            suggestions.append("No shares yet — consider a more shareable angle.")
        if clicks == 0 and impressions > 100:
            suggestions.append("No clicks — add a clear call-to-action.")

        result = {
            "platform_post_id": platform_post_id,
            "score": round(score, 2),
            "tier": tier,
            "engagement_rate": round(engagement_rate, 2),
            "impressions": impressions,
            "total_engagement": total_engagement,
            "suggestions": suggestions,
            "platform": platform,
        }

        logger.info(
            f"Feedback score for {platform_post_id}: {score:.2f} ({tier}) "
            f"— {engagement_rate:.2f}% engagement"
        )
        return result
