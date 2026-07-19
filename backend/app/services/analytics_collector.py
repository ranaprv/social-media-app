"""Analytics data collection from social platforms — fetches real performance data."""
import logging
import httpx
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.content import Post, PlatformConnection, AnalyticsMetric

logger = logging.getLogger(__name__)


async def collect_analytics_for_workspace(workspace_id: str):
    """Fetch analytics from connected platforms and store in database."""
    logger.info(f"Collecting analytics for workspace {workspace_id}")

    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(PlatformConnection).where(
                    PlatformConnection.workspace_id == workspace_id
                )
            )
            connections = result.scalars().all()

            for conn in connections:
                metrics = await _fetch_platform_metrics(conn)
                for metric_data in metrics:
                    # Upsert: update if exists, insert if new
                    existing = await db.execute(
                        select(AnalyticsMetric).where(
                            AnalyticsMetric.post_id == metric_data["post_id"],
                            AnalyticsMetric.platform == conn.platform,
                        )
                    )
                    existing_metric = existing.scalar_one_or_none()

                    if existing_metric:
                        existing_metric.impressions = metric_data.get("impressions", existing_metric.impressions)
                        existing_metric.reach = metric_data.get("reach", existing_metric.reach)
                        existing_metric.engagement = metric_data.get("engagement", existing_metric.engagement)
                        existing_metric.likes = metric_data.get("likes", existing_metric.likes)
                        existing_metric.comments = metric_data.get("comments", existing_metric.comments)
                        existing_metric.shares = metric_data.get("shares", existing_metric.shares)
                        existing_metric.clicks = metric_data.get("clicks", existing_metric.clicks)
                        existing_metric.recorded_at = datetime.utcnow()
                    else:
                        metric = AnalyticsMetric(
                            post_id=metric_data["post_id"],
                            platform=conn.platform,
                            impressions=metric_data.get("impressions", 0),
                            reach=metric_data.get("reach", 0),
                            engagement=metric_data.get("engagement", 0),
                            likes=metric_data.get("likes", 0),
                            comments=metric_data.get("comments", 0),
                            shares=metric_data.get("shares", 0),
                            clicks=metric_data.get("clicks", 0),
                        )
                        db.add(metric)

            await db.commit()
            logger.info(f"Analytics collection complete for workspace {workspace_id}")

    except Exception as e:
        logger.error(f"Analytics collection failed: {e}")


async def _fetch_platform_metrics(connection: PlatformConnection) -> list[dict]:
    """Fetch metrics from a specific platform API."""
    platform = connection.platform
    token = connection.access_token

    try:
        if platform == "linkedin":
            return await _fetch_linkedin(token)
        elif platform == "x":
            return await _fetch_twitter(token)
        elif platform == "instagram":
            return await _fetch_instagram(token)
        elif platform == "facebook":
            return await _fetch_facebook(token)
        elif platform == "youtube":
            return await _fetch_youtube(token)
    except Exception as e:
        logger.error(f"Failed to fetch {platform} metrics: {e}")

    return []


async def _fetch_linkedin(token: str) -> list[dict]:
    """Fetch LinkedIn post statistics via Marketing API."""
    metrics = []
    try:
        async with httpx.AsyncClient() as client:
            # Get organization shares
            resp = await client.get(
                "https://api.linkedin.com/v2/organizationalEntityShareStatistics",
                headers={"Authorization": f"Bearer {token}"},
                params={"q": "organizationalEntity", "orgId": "urn:li:organization:0"},
            )
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("elements", []):
                    metrics.append({
                        "post_id": item.get("shareShareStatistics", {}).get("share", "unknown"),
                        "impressions": item.get("totalShareStatistics", {}).get("impressionCount", 0),
                        "reach": item.get("totalShareStatistics", {}).get("uniqueImpressionsCount", 0),
                        "engagement": item.get("totalShareStatistics", {}).get("clickCount", 0),
                        "likes": item.get("totalShareStatistics", {}).get("likeCount", 0),
                        "comments": item.get("totalShareStatistics", {}).get("commentCount", 0),
                        "shares": item.get("totalShareStatistics", {}).get("shareCount", 0),
                        "clicks": item.get("totalShareStatistics", {}).get("clickCount", 0),
                    })
    except Exception as e:
        logger.error(f"LinkedIn API error: {e}")
    return metrics


async def _fetch_twitter(token: str) -> list[dict]:
    """Fetch Twitter/X tweet metrics via v2 API."""
    metrics = []
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.twitter.com/2/users/me/tweets",
                headers={"Authorization": f"Bearer {token}"},
                params={"tweet.fields": "public_metrics", "max_results": 100},
            )
            if resp.status_code == 200:
                data = resp.json()
                for tweet in data.get("data", []):
                    pm = tweet.get("public_metrics", {})
                    metrics.append({
                        "post_id": tweet.get("id", "unknown"),
                        "impressions": pm.get("impression_count", 0),
                        "reach": 0,  # Twitter v2 doesn't provide reach directly
                        "engagement": pm.get("like_count", 0) + pm.get("retweet_count", 0) + pm.get("reply_count", 0),
                        "likes": pm.get("like_count", 0),
                        "comments": pm.get("reply_count", 0),
                        "shares": pm.get("retweet_count", 0) + pm.get("quote_count", 0),
                        "clicks": pm.get("url_link_clicks", 0),
                    })
    except Exception as e:
        logger.error(f"Twitter API error: {e}")
    return metrics


async def _fetch_instagram(token: str) -> list[dict]:
    """Fetch Instagram media insights via Graph API."""
    metrics = []
    try:
        async with httpx.AsyncClient() as client:
            # Get media list
            resp = await client.get(
                "https://graph.facebook.com/v18.0/me/media",
                params={"fields": "id,caption,insights.metric(impressions,reach,engagement,likes,comments,shares,saves)", "access_token": token},
            )
            if resp.status_code == 200:
                data = resp.json()
                for media in data.get("data", []):
                    insights = {}
                    for insight in media.get("insights", {}).get("data", []):
                        insights[insight["name"]] = insight.get("values", [{}])[0].get("value", 0)
                    metrics.append({
                        "post_id": media.get("id", "unknown"),
                        "impressions": insights.get("impressions", 0),
                        "reach": insights.get("reach", 0),
                        "engagement": insights.get("engagement", 0),
                        "likes": insights.get("likes", 0),
                        "comments": insights.get("comments", 0),
                        "shares": insights.get("shares", 0),
                        "clicks": 0,
                    })
    except Exception as e:
        logger.error(f"Instagram API error: {e}")
    return metrics


async def _fetch_facebook(token: str) -> list[dict]:
    """Fetch Facebook post insights via Graph API."""
    metrics = []
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://graph.facebook.com/v18.0/me/posts",
                params={"fields": "id,insights.metric(post_impressions,post_reactions_by_type_total,post_clicks,post_shares)", "access_token": token},
            )
            if resp.status_code == 200:
                data = resp.json()
                for post in data.get("data", []):
                    insights = {}
                    for insight in post.get("insights", {}).get("data", []):
                        insights[insight["name"]] = insight.get("values", [{}])[0].get("value", 0)
                    reactions = insights.get("post_reactions_by_type_total", {})
                    total_reactions = sum(reactions.values()) if isinstance(reactions, dict) else 0
                    metrics.append({
                        "post_id": post.get("id", "unknown"),
                        "impressions": insights.get("post_impressions", 0),
                        "reach": 0,
                        "engagement": total_reactions,
                        "likes": total_reactions,
                        "comments": 0,
                        "shares": insights.get("post_shares", 0),
                        "clicks": insights.get("post_clicks", 0),
                    })
    except Exception as e:
        logger.error(f"Facebook API error: {e}")
    return metrics


async def _fetch_youtube(token: str) -> list[dict]:
    """Fetch YouTube video statistics via Data API v3 — uses OAuth bearer token."""
    metrics = []
    try:
        async with httpx.AsyncClient() as client:
            # Use Authorization header (OAuth), not key parameter
            resp = await client.get(
                "https://www.googleapis.com/youtube/v3/search",
                params={
                    "part": "id",
                    "forMine": "true",
                    "type": "video",
                    "maxResults": "50",
                },
                headers={
                    "Authorization": f"Bearer {token}",
                },
            )
            if resp.status_code == 200:
                video_ids = [item["id"]["videoId"] for item in resp.json().get("items", [])]
                if video_ids:
                    stats_resp = await client.get(
                        "https://www.googleapis.com/youtube/v3/videos",
                        params={
                            "part": "statistics,contentDetails",
                            "id": ",".join(video_ids[:50]),
                        },
                        headers={
                            "Authorization": f"Bearer {token}",
                        },
                    )
                    if stats_resp.status_code == 200:
                        for video in stats_resp.json().get("items", []):
                            stats = video.get("statistics", {})
                            metrics.append({
                                "post_id": video.get("id", "unknown"),
                                "impressions": int(stats.get("viewCount", 0)),
                                "reach": int(stats.get("viewCount", 0)),
                                "engagement": int(stats.get("likeCount", 0)) + int(stats.get("commentCount", 0)),
                                "likes": int(stats.get("likeCount", 0)),
                                "comments": int(stats.get("commentCount", 0)),
                                "shares": 0,
                                "clicks": int(stats.get("favoriteCount", 0)),
                            })
            elif resp.status_code == 401:
                logger.warning("YouTube analytics: OAuth token expired or invalid")
            else:
                logger.warning("YouTube analytics search failed: %s %s", resp.status_code, resp.text[:200])
    except Exception as e:
        logger.error(f"YouTube API error: {e}")
    return metrics
