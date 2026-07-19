"""Advanced analytics report generator — PDF/HTML reports.

Generates comprehensive analytics reports with charts and insights.
"""
import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post, AnalyticsMetric
from app.models.post_platform import PostPlatform

logger = logging.getLogger(__name__)


async def generate_analytics_report(
    db: AsyncSession,
    workspace_id: str,
    days: int = 30,
    report_format: str = "html",
) -> dict[str, Any]:
    """Generate a comprehensive analytics report."""
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Gather data
    summary = await _get_summary_data(db, workspace_id, cutoff)
    platform_data = await _get_platform_data(db, workspace_id, cutoff)
    top_posts = await _get_top_posts(db, workspace_id, cutoff)
    trends = await _get_trend_data(db, workspace_id, cutoff)

    # Build report
    report = {
        "title": f"Social Media Analytics Report — Last {days} Days",
        "generated_at": datetime.utcnow().isoformat(),
        "period": {"days": days, "start": cutoff.isoformat(), "end": datetime.utcnow().isoformat()},
        "summary": summary,
        "platforms": platform_data,
        "top_posts": top_posts,
        "trends": trends,
        "insights": _generate_insights(summary, platform_data, top_posts),
        "format": report_format,
    }

    if report_format == "html":
        report["html"] = _render_html_report(report)
    elif report_format == "json":
        pass  # Already structured

    return report


async def _get_summary_data(db: AsyncSession, workspace_id: str, cutoff: datetime) -> dict:
    """Get summary metrics."""
    result = await db.execute(
        select(
            func.sum(AnalyticsMetric.impressions),
            func.sum(AnalyticsMetric.engagement),
            func.sum(AnalyticsMetric.reach),
            func.sum(AnalyticsMetric.clicks),
            func.count(PostPlatform.id),
        )
        .join(Post, Post.id == AnalyticsMetric.post_id)
        .where(Post.workspace_id == workspace_id, AnalyticsMetric.recorded_at >= cutoff)
    )
    row = result.one()

    total_imp = row[0] or 0
    total_eng = row[1] or 0
    total_reach = row[2] or 0
    total_clicks = row[3] or 0
    total_posts = row[4] or 0

    return {
        "total_impressions": total_imp,
        "total_engagement": total_eng,
        "total_reach": total_reach,
        "total_clicks": total_clicks,
        "total_posts": total_posts,
        "avg_engagement_rate": round((total_eng / total_imp * 100) if total_imp > 0 else 0, 2),
        "avg_impressions_per_post": round(total_imp / max(total_posts, 1)),
        "avg_engagement_per_post": round(total_eng / max(total_posts, 1)),
    }


async def _get_platform_data(db: AsyncSession, workspace_id: str, cutoff: datetime) -> dict:
    """Get per-platform data."""
    result = await db.execute(
        select(
            AnalyticsMetric.platform,
            func.sum(AnalyticsMetric.impressions),
            func.sum(AnalyticsMetric.engagement),
            func.count(AnalyticsMetric.id),
        )
        .join(Post, Post.id == AnalyticsMetric.post_id)
        .where(Post.workspace_id == workspace_id, AnalyticsMetric.recorded_at >= cutoff)
        .group_by(AnalyticsMetric.platform)
    )

    platforms = {}
    for row in result.all():
        platform, imp, eng, count = row
        platforms[platform] = {
            "impressions": imp or 0,
            "engagement": eng or 0,
            "posts": count or 0,
            "engagement_rate": round(((eng or 0) / (imp or 1)) * 100, 2),
        }

    return platforms


async def _get_top_posts(db: AsyncSession, workspace_id: str, cutoff: datetime) -> list:
    """Get top performing posts."""
    result = await db.execute(
        select(
            Post.id, Post.title, Post.platform,
            func.sum(AnalyticsMetric.engagement).label("engagement"),
        )
        .join(AnalyticsMetric, Post.id == AnalyticsMetric.post_id)
        .where(Post.workspace_id == workspace_id, Post.published_at >= cutoff)
        .group_by(Post.id)
        .order_by(func.sum(AnalyticsMetric.engagement).desc())
        .limit(10)
    )

    return [
        {"id": r[0], "title": r[1], "platform": r[2], "engagement": r[3] or 0}
        for r in result.all()
    ]


async def _get_trend_data(db: AsyncSession, workspace_id: str, cutoff: datetime) -> dict:
    """Get daily trend data."""
    result = await db.execute(
        select(
            func.date(AnalyticsMetric.recorded_at),
            func.sum(AnalyticsMetric.engagement),
            func.sum(AnalyticsMetric.impressions),
        )
        .join(Post, Post.id == AnalyticsMetric.post_id)
        .where(Post.workspace_id == workspace_id, AnalyticsMetric.recorded_at >= cutoff)
        .group_by(func.date(AnalyticsMetric.recorded_at))
        .order_by(func.date(AnalyticsMetric.recorded_at))
    )

    return {
        "daily": [
            {"date": str(r[0]), "engagement": r[1] or 0, "impressions": r[2] or 0}
            for r in result.all()
        ]
    }


def _generate_insights(summary: dict, platforms: dict, top_posts: list) -> list[str]:
    """Generate actionable insights from data."""
    insights: list[str] = []

    if summary["avg_engagement_rate"] > 5:
        insights.append("Strong engagement rate — content resonates well with audience")
    elif summary["avg_engagement_rate"] < 2:
        insights.append("Low engagement rate — consider testing different content formats")

    # Best platform
    if platforms:
        best = max(platforms.items(), key=lambda x: x[1]["engagement_rate"])
        worst = min(platforms.items(), key=lambda x: x[1]["engagement_rate"])
        insights.append(f"Best performing platform: {best[0]} ({best[1]['engagement_rate']}% engagement)")
        if best[0] != worst[0]:
            insights.append(f"Consider investing more in {best[0]} — it outperforms {worst[0]}")

    if summary["total_posts"] < 10:
        insights.append("Low posting volume — increase frequency for better reach")

    return insights


def _render_html_report(report: dict) -> str:
    """Render report as HTML."""
    html = f"""<!DOCTYPE html>
<html><head><title>{report['title']}</title>
<style>body{{font-family:sans-serif;max-width:800px;margin:0 auto;padding:20px}}
table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #ddd;padding:8px;text-align:left}}
th{{background:#f5f5f5}}.metric{{font-size:24px;font-weight:bold}}</style></head>
<body>
<h1>{report['title']}</h1>
<p>Generated: {report['generated_at']}</p>
<h2>Summary</h2>
<table><tr><td>Total Impressions</td><td>{report['summary']['total_impressions']:,}</td></tr>
<tr><td>Total Engagement</td><td>{report['summary']['total_engagement']:,}</td></tr>
<tr><td>Avg Engagement Rate</td><td>{report['summary']['avg_engagement_rate']}%</td></tr></table>
<h2>Platforms</h2>
<table><tr><th>Platform</th><th>Impressions</th><th>Engagement</th><th>Rate</th></tr>"""
    for p, d in report.get("platforms", {}).items():
        html += f"<tr><td>{p}</td><td>{d['impressions']:,}</td><td>{d['engagement']:,}</td><td>{d['engagement_rate']}%</td></tr>"
    html += "</table><h2>Insights</h2><ul>"
    for insight in report.get("insights", []):
        html += f"<li>{insight}</li>"
    html += "</ul></body></html>"
    return html
