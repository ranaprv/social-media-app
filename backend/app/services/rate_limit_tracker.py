"""Rate limit tracker — per-platform quota tracking and throttling.

Tracks API call counts, detects rate limit headers, and prevents
exceeding platform quotas.
"""
import logging
import time
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)

# Platform rate limit configurations
PLATFORM_RATE_LIMITS: dict[str, dict[str, Any]] = {
    "linkedin": {
        "daily_limit": 100,  # posts per day
        "window": "daily",
        "reset_hour_utc": 0,
        "notes": "100 posts/day per organization",
    },
    "x": {
        "daily_limit": 50,  # tweets per day (free tier)
        "window": "daily",
        "reset_hour_utc": 0,
        "notes": "Free: 50 tweets/day, 1500/month. Pro: 3000/month.",
        "v2_post_limit": 200,  # per 15 min window
    },
    "instagram": {
        "daily_limit": 25,  # posts per day
        "window": "daily",
        "reset_hour_utc": 0,
        "notes": "25 posts/day via API. Rate limit: 200 calls/hour.",
        "hourly_api_limit": 200,
    },
    "facebook": {
        "daily_limit": 25,  # posts per page per day
        "window": "daily",
        "reset_hour_utc": 0,
        "notes": "25 posts/page/day. API: 200 calls/user/hour.",
        "hourly_api_limit": 200,
    },
    "youtube": {
        "daily_limit": 6,  # videos per day
        "window": "daily",
        "reset_hour_utc": 0,
        "notes": "6 video uploads/day. 10,000 quota units/day.",
        "quota_units": 10000,
        "upload_cost_units": 1600,
    },
}

# In-memory rate limit tracking (production: use Redis)
_rate_store: dict[str, dict[str, Any]] = {}


def get_rate_limit_info(platform: str) -> dict[str, Any]:
    """Get rate limit configuration for a platform."""
    config = PLATFORM_RATE_LIMITS.get(platform, {})
    tracking = _rate_store.get(platform, {})

    used_today = tracking.get("daily_count", 0)
    daily_limit = config.get("daily_limit", 0)
    remaining = max(0, daily_limit - used_today)

    return {
        "platform": platform,
        "daily_limit": daily_limit,
        "used_today": used_today,
        "remaining": remaining,
        "reset_at": tracking.get("reset_at"),
        "is_throttled": remaining == 0,
        "notes": config.get("notes", ""),
    }


def check_rate_limit(platform: str) -> dict[str, Any]:
    """Check if we can make another API call to a platform.

    Returns whether the call is allowed and when to retry if not.
    """
    info = get_rate_limit_info(platform)

    if info["is_throttled"]:
        reset_at = info.get("reset_at")
        wait_seconds = 0
        if reset_at:
            try:
                reset_dt = datetime.fromisoformat(reset_at)
                wait_seconds = max(0, (reset_dt - datetime.utcnow()).total_seconds())
            except ValueError:
                wait_seconds = 3600  # Default 1 hour

        return {
            "allowed": False,
            "reason": "daily_limit_reached",
            "retry_after_seconds": round(wait_seconds),
            "retry_at": reset_at,
            "remaining": 0,
        }

    return {
        "allowed": True,
        "remaining": info["remaining"],
        "daily_limit": info["daily_limit"],
    }


def record_api_call(platform: str, success: bool = True) -> dict[str, Any]:
    """Record an API call to a platform.

    Should be called after every platform API interaction.
    """
    today = datetime.utcnow().strftime("%Y-%m-%d")

    if platform not in _rate_store:
        _rate_store[platform] = {"daily_count": 0, "date": today, "reset_at": None}

    tracking = _rate_store[platform]

    # Reset if new day
    if tracking.get("date") != today:
        tracking["daily_count"] = 0
        tracking["date"] = today
        # Set reset time to midnight UTC
        tomorrow = datetime.utcnow().replace(hour=0, minute=0, second=0) + timedelta(days=1)
        tracking["reset_at"] = tomorrow.isoformat()

    tracking["daily_count"] = tracking.get("daily_count", 0) + 1
    tracking["last_call"] = datetime.utcnow().isoformat()
    tracking["last_success"] = success

    # Check if we're approaching the limit
    config = PLATFORM_RATE_LIMITS.get(platform, {})
    daily_limit = config.get("daily_limit", 0)
    remaining = max(0, daily_limit - tracking["daily_count"])

    if remaining <= 5 and remaining > 0:
        logger.warning(
            f"Platform {platform} approaching daily limit: {remaining} remaining"
        )

    return {
        "platform": platform,
        "daily_count": tracking["daily_count"],
        "remaining": remaining,
        "approaching_limit": remaining <= 5 and remaining > 0,
    }


def record_rate_limit_hit(platform: str, retry_after: int = 3600) -> dict[str, Any]:
    """Record that we hit a rate limit on a platform.

    Called when we receive a 429 response from a platform API.
    """
    if platform not in _rate_store:
        _rate_store[platform] = {}

    _rate_store[platform]["throttled_until"] = (
        datetime.utcnow() + timedelta(seconds=retry_after)
    ).isoformat()
    _rate_store[platform]["throttle_reason"] = "429_rate_limit"

    logger.warning(
        f"Rate limit hit on {platform}. Throttled for {retry_after}s"
    )

    return {
        "platform": platform,
        "throttled": True,
        "retry_after_seconds": retry_after,
        "throttled_until": _rate_store[platform]["throttled_until"],
    }


def get_all_rate_status() -> dict[str, Any]:
    """Get rate limit status for all platforms."""
    return {
        platform: get_rate_limit_info(platform)
        for platform in PLATFORM_RATE_LIMITS
    }


def get_throttled_platforms() -> list[dict[str, Any]]:
    """Get list of platforms currently throttled."""
    throttled = []
    for platform, tracking in _rate_store.items():
        throttled_until = tracking.get("throttled_until")
        if throttled_until:
            try:
                until_dt = datetime.fromisoformat(throttled_until)
                if until_dt > datetime.utcnow():
                    remaining = (until_dt - datetime.utcnow()).total_seconds()
                    throttled.append({
                        "platform": platform,
                        "throttled_until": throttled_until,
                        "remaining_seconds": round(remaining),
                    })
            except ValueError:
                pass
    return throttled
