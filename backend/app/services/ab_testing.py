"""A/B content testing — schedule variant posts and track winner selection.

Creates multiple PostPlatform variants for the same post+platform,
tracks engagement, and recommends the winning variant.
"""
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post, AnalyticsMetric
from app.models.post_platform import PostPlatform

logger = logging.getLogger(__name__)


async def create_ab_test(
    db: AsyncSession,
    workspace_id: str,
    post_id: str,
    platform: str,
    variants: list[dict[str, str]],
    test_duration_hours: int = 24,
) -> dict[str, Any]:
    """Create an A/B test with multiple caption variants.

    Each variant gets its own PostPlatform entry. They are scheduled
    at staggered times within the test window.

    Args:
        variants: List of {"caption": "...", "label": "Variant A"} dicts.
        test_duration_hours: How long the test runs before winner selection.

    Returns:
        Test metadata with variant IDs.
    """
    # Verify post exists
    post_result = await db.execute(
        select(Post).where(Post.id == post_id, Post.status == "published")
    )
    post = post_result.scalar_one_none()
    if not post:
        # Try drafts/scheduled
        post_result = await db.execute(
            select(Post).where(Post.id == post_id, Post.workspace_id == workspace_id)
        )
        post = post_result.scalar_one_none()
    if not post:
        return {"error": f"Post {post_id} not found"}

    test_id = str(uuid.uuid4())
    now = datetime.utcnow()
    stagger_minutes = test_duration_hours * 60 // max(len(variants), 1)

    created_variants = []
    for i, variant in enumerate(variants):
        pp = PostPlatform(
            id=str(uuid.uuid4()),
            post_id=post_id,
            workspace_id=workspace_id,
            platform=platform,
            caption=variant.get("caption", post.content),
            status="scheduled",
            scheduled_at=now + timedelta(minutes=stagger_minutes * (i + 1)),
            meta={
                "ab_test_id": test_id,
                "variant_label": variant.get("label", f"Variant {chr(65 + i)}"),
                "variant_index": i,
                "test_start": now.isoformat(),
                "test_end": (now + timedelta(hours=test_duration_hours)).isoformat(),
            },
        )
        db.add(pp)
        created_variants.append({
            "id": pp.id,
            "label": variant.get("label", f"Variant {chr(65 + i)}"),
            "caption_preview": (variant.get("caption", post.content) or "")[:100],
            "scheduled_at": pp.scheduled_at.isoformat(),
        })

    await db.flush()

    return {
        "test_id": test_id,
        "platform": platform,
        "post_id": post_id,
        "variants": created_variants,
        "test_duration_hours": test_duration_hours,
        "status": "created",
    }


async def get_ab_test_results(
    db: AsyncSession,
    test_id: str,
) -> dict[str, Any]:
    """Get A/B test results by comparing variant performance.

    Queries analytics for all PostPlatform entries with the same ab_test_id
    and returns engagement comparison.
    """
    # Find all variants for this test
    result = await db.execute(
        select(PostPlatform).where(
            PostPlatform.meta["ab_test_id"].astext == test_id,
        )
    )
    variants = result.scalars().all()

    if not variants:
        return {"error": f"Test {test_id} not found"}

    # Get analytics for each variant
    variant_results = []
    for v in variants:
        analytics_result = await db.execute(
            select(
                func.sum(AnalyticsMetric.engagement).label("engagement"),
                func.sum(AnalyticsMetric.impressions).label("impressions"),
                func.sum(AnalyticsMetric.reach).label("reach"),
                func.sum(AnalyticsMetric.clicks).label("clicks"),
                func.count(AnalyticsMetric.id).label("data_points"),
            ).where(AnalyticsMetric.post_id == v.post_id)
        )
        metrics = analytics_result.one()

        eng_rate = 0
        if metrics.impressions and metrics.impressions > 0:
            eng_rate = (metrics.engagement or 0) / metrics.impressions * 100

        variant_results.append({
            "variant_id": v.id,
            "label": (v.meta or {}).get("variant_label", "Unknown"),
            "status": v.status,
            "engagement": metrics.engagement or 0,
            "impressions": metrics.impressions or 0,
            "reach": metrics.reach or 0,
            "clicks": metrics.clicks or 0,
            "engagement_rate": round(eng_rate, 2),
            "data_points": metrics.data_points or 0,
            "published_at": v.published_at.isoformat() if v.published_at else None,
        })

    # Sort by engagement rate
    variant_results.sort(key=lambda x: x["engagement_rate"], reverse=True)

    winner = variant_results[0] if variant_results else None

    return {
        "test_id": test_id,
        "platform": variants[0].platform if variants else None,
        "variants": variant_results,
        "winner": winner,
        "recommendation": (
            f"Variant '{winner['label']}' leads with {winner['engagement_rate']}% engagement rate"
            if winner and winner["data_points"] > 0
            else "Not enough data yet — wait for more posts to be published"
        ),
    }
