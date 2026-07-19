"""Platform health monitor — check API status and rate limits.

Pings platform APIs to verify connectivity and tracks rate limit usage.
"""
import logging
import httpx
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


async def check_platform_health(platform: str, access_token: str = "") -> dict[str, Any]:
    """Check the health/connectivity of a platform's API.

    Returns status, latency, and any rate limit info.
    """
    start = datetime.utcnow()

    checks = {
        "linkedin": _check_linkedin,
        "x": _check_twitter,
        "facebook": _check_facebook,
        "instagram": _check_instagram,
        "youtube": _check_youtube,
    }

    checker = checks.get(platform)
    if not checker:
        return {
            "platform": platform,
            "status": "unknown",
            "error": f"No health check for {platform}",
        }

    try:
        result = await checker(access_token)
        elapsed = (datetime.utcnow() - start).total_seconds() * 1000
        result["latency_ms"] = round(elapsed, 0)
        result["checked_at"] = datetime.utcnow().isoformat()
        return result
    except Exception as e:
        elapsed = (datetime.utcnow() - start).total_seconds() * 1000
        return {
            "platform": platform,
            "status": "error",
            "error": str(e),
            "latency_ms": round(elapsed, 0),
            "checked_at": datetime.utcnow().isoformat(),
        }


async def check_all_platforms(connections: dict[str, str]) -> dict[str, Any]:
    """Check health for all connected platforms.

    Args:
        connections: {platform: access_token} dict.

    Returns per-platform health status.
    """
    results = {}
    for platform, token in connections.items():
        results[platform] = await check_platform_health(platform, token)
    return results


async def _check_linkedin(token: str) -> dict[str, Any]:
    """Check LinkedIn API connectivity."""
    if not token:
        return {"platform": "linkedin", "status": "no_token", "message": "Not connected"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                "https://api.linkedin.com/v2/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "platform": "linkedin",
                    "status": "healthy",
                    "message": f"Connected as {data.get('localizedFirstName', 'user')}",
                }
            elif response.status_code == 401:
                return {"platform": "linkedin", "status": "token_expired", "message": "Token expired — refresh needed"}
            elif response.status_code == 429:
                return {"platform": "linkedin", "status": "rate_limited", "message": "Rate limited"}
            else:
                return {"platform": "linkedin", "status": "error", "message": f"HTTP {response.status_code}"}
    except httpx.TimeoutException:
        return {"platform": "linkedin", "status": "timeout", "message": "API timeout"}


async def _check_twitter(token: str) -> dict[str, Any]:
    """Check X/Twitter API connectivity."""
    if not token:
        return {"platform": "x", "status": "no_token", "message": "Not connected"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                "https://api.twitter.com/2/users/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            if response.status_code == 200:
                data = response.json()
                username = data.get("data", {}).get("username", "user")
                return {
                    "platform": "x",
                    "status": "healthy",
                    "message": f"Connected as @{username}",
                }
            elif response.status_code == 401:
                return {"platform": "x", "status": "token_expired", "message": "Token expired"}
            elif response.status_code == 429:
                reset = response.headers.get("x-rate-limit-reset", "")
                return {
                    "platform": "x",
                    "status": "rate_limited",
                    "message": f"Rate limited. Resets: {reset}",
                    "rate_limit_reset": reset,
                }
            else:
                return {"platform": "x", "status": "error", "message": f"HTTP {response.status_code}"}
    except httpx.TimeoutException:
        return {"platform": "x", "status": "timeout", "message": "API timeout"}


async def _check_facebook(token: str) -> dict[str, Any]:
    """Check Facebook Graph API connectivity."""
    if not token:
        return {"platform": "facebook", "status": "no_token", "message": "Not connected"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                "https://graph.facebook.com/v19.0/me",
                params={"access_token": token},
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "platform": "facebook",
                    "status": "healthy",
                    "message": f"Connected as {data.get('name', 'user')}",
                }
            elif response.status_code == 401:
                return {"platform": "facebook", "status": "token_expired", "message": "Token expired"}
            else:
                error = response.json().get("error", {})
                return {
                    "platform": "facebook",
                    "status": "error",
                    "message": error.get("message", f"HTTP {response.status_code}"),
                }
    except httpx.TimeoutException:
        return {"platform": "facebook", "status": "timeout", "message": "API timeout"}


async def _check_instagram(token: str) -> dict[str, Any]:
    """Check Instagram Graph API connectivity (uses Facebook token)."""
    if not token:
        return {"platform": "instagram", "status": "no_token", "message": "Not connected"}

    # Instagram check requires a page token + IG user ID
    # For basic check, verify the token is valid via Facebook
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                "https://graph.facebook.com/v19.0/me",
                params={"access_token": token},
            )
            if response.status_code == 200:
                return {
                    "platform": "instagram",
                    "status": "healthy",
                    "message": "Token valid (check IG user ID for full verification)",
                }
            elif response.status_code == 401:
                return {"platform": "instagram", "status": "token_expired", "message": "Token expired"}
            else:
                return {"platform": "instagram", "status": "error", "message": f"HTTP {response.status_code}"}
    except httpx.TimeoutException:
        return {"platform": "instagram", "status": "timeout", "message": "API timeout"}


async def _check_youtube(token: str) -> dict[str, Any]:
    """Check YouTube Data API connectivity."""
    if not token:
        return {"platform": "youtube", "status": "no_token", "message": "Not connected"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                "https://www.googleapis.com/youtube/v3/channels",
                params={"part": "snippet", "mine": True, "access_token": token},
            )
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                if items:
                    title = items[0].get("snippet", {}).get("title", "channel")
                    return {
                        "platform": "youtube",
                        "status": "healthy",
                        "message": f"Connected to {title}",
                    }
                return {
                    "platform": "youtube",
                    "status": "healthy",
                    "message": "Token valid (no channel found)",
                }
            elif response.status_code == 401:
                return {"platform": "youtube", "status": "token_expired", "message": "Token expired"}
            else:
                return {"platform": "youtube", "status": "error", "message": f"HTTP {response.status_code}"}
    except httpx.TimeoutException:
        return {"platform": "youtube", "status": "timeout", "message": "API timeout"}
