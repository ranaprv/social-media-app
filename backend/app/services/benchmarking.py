"""Content performance benchmarking — compare against industry averages.

Provides industry-specific benchmarks for engagement rates, posting
frequency, and content performance.
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Industry benchmarks (approximate 2024-2025 data)
INDUSTRY_BENCHMARKS = {
    "technology": {
        "linkedin": {"avg_engagement_rate": 3.5, "avg_post_frequency": 4, "avg_reach": 800},
        "x": {"avg_engagement_rate": 1.5, "avg_post_frequency": 7, "avg_reach": 500},
        "instagram": {"avg_engagement_rate": 4.2, "avg_post_frequency": 5, "avg_reach": 1200},
        "facebook": {"avg_engagement_rate": 1.8, "avg_post_frequency": 3, "avg_reach": 600},
        "youtube": {"avg_engagement_rate": 5.0, "avg_post_frequency": 2, "avg_reach": 2000},
    },
    "marketing": {
        "linkedin": {"avg_engagement_rate": 4.0, "avg_post_frequency": 5, "avg_reach": 1000},
        "x": {"avg_engagement_rate": 2.0, "avg_post_frequency": 10, "avg_reach": 600},
        "instagram": {"avg_engagement_rate": 5.5, "avg_post_frequency": 7, "avg_reach": 1500},
        "facebook": {"avg_engagement_rate": 2.2, "avg_post_frequency": 4, "avg_reach": 700},
        "youtube": {"avg_engagement_rate": 4.5, "avg_post_frequency": 3, "avg_reach": 1800},
    },
    "ecommerce": {
        "linkedin": {"avg_engagement_rate": 2.8, "avg_post_frequency": 3, "avg_reach": 600},
        "x": {"avg_engagement_rate": 1.2, "avg_post_frequency": 5, "avg_reach": 400},
        "instagram": {"avg_engagement_rate": 6.0, "avg_post_frequency": 8, "avg_reach": 2000},
        "facebook": {"avg_engagement_rate": 2.5, "avg_post_frequency": 4, "avg_reach": 800},
        "youtube": {"avg_engagement_rate": 3.8, "avg_post_frequency": 2, "avg_reach": 1500},
    },
    "healthcare": {
        "linkedin": {"avg_engagement_rate": 3.2, "avg_post_frequency": 3, "avg_reach": 700},
        "x": {"avg_engagement_rate": 1.8, "avg_post_frequency": 5, "avg_reach": 500},
        "instagram": {"avg_engagement_rate": 3.5, "avg_post_frequency": 4, "avg_reach": 1000},
        "facebook": {"avg_engagement_rate": 2.0, "avg_post_frequency": 3, "avg_reach": 600},
        "youtube": {"avg_engagement_rate": 4.2, "avg_post_frequency": 1, "avg_reach": 1200},
    },
    "finance": {
        "linkedin": {"avg_engagement_rate": 3.8, "avg_post_frequency": 4, "avg_reach": 900},
        "x": {"avg_engagement_rate": 1.6, "avg_post_frequency": 6, "avg_reach": 550},
        "instagram": {"avg_engagement_rate": 3.0, "avg_post_frequency": 4, "avg_reach": 800},
        "facebook": {"avg_engagement_rate": 1.5, "avg_post_frequency": 3, "avg_reach": 500},
        "youtube": {"avg_engagement_rate": 4.0, "avg_post_frequency": 2, "avg_reach": 1400},
    },
}


def get_benchmarks(industry: str, platform: str | None = None) -> dict[str, Any]:
    """Get industry benchmarks."""
    industry_data = INDUSTRY_BENCHMARKS.get(industry, {})
    if not industry_data:
        return {"error": f"No benchmarks for industry: {industry}"}

    if platform:
        platform_data = industry_data.get(platform, {})
        if not platform_data:
            return {"error": f"No benchmarks for {platform} in {industry}"}
        return {
            "industry": industry,
            "platform": platform,
            "benchmarks": platform_data,
        }

    return {
        "industry": industry,
        "platforms": industry_data,
    }


def compare_to_benchmark(
    your_metrics: dict[str, float],
    industry: str,
    platform: str,
) -> dict[str, Any]:
    """Compare your metrics against industry benchmarks."""
    benchmarks = INDUSTRY_BENCHMARKS.get(industry, {}).get(platform, {})
    if not benchmarks:
        return {"error": f"No benchmarks available"}

    comparisons: list[dict[str, Any]] = []

    for metric, benchmark_value in benchmarks.items():
        your_value = your_metrics.get(metric, 0)
        if benchmark_value > 0:
            diff_pct = ((your_value - benchmark_value) / benchmark_value) * 100
        else:
            diff_pct = 0

        if diff_pct > 20:
            status = "above_average"
        elif diff_pct > -20:
            status = "average"
        else:
            status = "below_average"

        comparisons.append({
            "metric": metric,
            "your_value": round(your_value, 2),
            "benchmark": round(benchmark_value, 2),
            "difference_pct": round(diff_pct, 1),
            "status": status,
        })

    overall_score = sum(
        100 if c["status"] == "above_average" else 50 if c["status"] == "average" else 20
        for c in comparisons
    ) / max(len(comparisons), 1)

    return {
        "industry": industry,
        "platform": platform,
        "comparisons": comparisons,
        "overall_score": round(overall_score),
        "verdict": "Outperforming" if overall_score > 70 else "Average" if overall_score > 40 else "Below Average",
    }


def get_available_industries() -> list[str]:
    """Get list of available industries."""
    return list(INDUSTRY_BENCHMARKS.keys())
