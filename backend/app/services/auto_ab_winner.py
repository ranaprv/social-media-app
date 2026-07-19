"""Auto A/B winner selection — pick winner based on metrics.

Automatically selects the winning variant from A/B tests based on
configurable metrics (engagement rate, reach, clicks, etc.).
"""
import logging
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import AnalyticsMetric
from app.models.post_platform import PostPlatform

logger = logging.getLogger(__name__)


async def auto_select_winner(
    db: AsyncSession,
    test_id: str,
    metric: str = "engagement_rate",
    min_data_points: int = 5,
) -> dict[str, Any]:
    """Automatically select the winning variant from an A/B test.

    Args:
        test_id: The A/B test ID (stored in PostPlatform.meta['ab_test_id']).
        metric: Which metric to use for selection.
        min_data_points: Minimum data points before auto-selecting.

    Returns winner recommendation with confidence level.
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
    variant_scores: list[dict[str, Any]] = []
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

        eng = metrics.engagement or 0
        imp = metrics.impressions or 0
        reach = metrics.reach or 0
        clicks = metrics.clicks or 0
        dp = metrics.data_points or 0

        # Calculate score based on selected metric
        if metric == "engagement_rate":
            score = (eng / imp * 100) if imp > 0 else 0
        elif metric == "reach":
            score = reach
        elif metric == "clicks":
            score = clicks
        elif metric == "engagement":
            score = eng
        else:
            score = (eng / imp * 100) if imp > 0 else 0

        variant_scores.append({
            "variant_id": v.id,
            "label": (v.meta or {}).get("variant_label", "Unknown"),
            "score": round(score, 2),
            "engagement": eng,
            "impressions": imp,
            "reach": reach,
            "clicks": clicks,
            "data_points": dp,
        })

    # Sort by score
    variant_scores.sort(key=lambda x: x["score"], reverse=True)

    if not variant_scores:
        return {"error": "No variants found"}

    winner = variant_scores[0]
    runner_up = variant_scores[1] if len(variant_scores) > 1 else None

    # Calculate confidence
    total_dp = sum(v["data_points"] for v in variant_scores)
    if total_dp < min_data_points:
        confidence = "low"
        recommendation = f"Not enough data ({total_dp}/{min_data_points} data points). Continue test."
    elif runner_up and winner["score"] > 0:
        margin = (winner["score"] - runner_up["score"]) / max(winner["score"], 1) * 100
        if margin > 20:
            confidence = "high"
            recommendation = f"Strong winner: {winner['label']} outperforms by {margin:.0f}%"
        elif margin > 5:
            confidence = "medium"
            recommendation = f"Likely winner: {winner['label']} leads by {margin:.0f}%"
        else:
            confidence = "low"
            recommendation = f"Close race. {winner['label']} leads by only {margin:.0f}%. Consider extending test."
    else:
        confidence = "medium"
        recommendation = f"Winner: {winner['label']}"

    return {
        "test_id": test_id,
        "metric": metric,
        "winner": winner,
        "all_variants": variant_scores,
        "confidence": confidence,
        "recommendation": recommendation,
        "total_data_points": total_dp,
    }
