"""Timezone-aware scheduling — detect audience timezone and schedule accordingly.

Provides timezone detection, conversion, and audience-aware scheduling.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger(__name__)

# Common audience timezone mappings by platform/region
AUDIENCE_TIMEZONES: dict[str, list[dict[str, Any]]] = {
    "linkedin": [
        {"region": "US East", "tz": "US/Eastern", "weight": 0.35},
        {"region": "US West", "tz": "US/Pacific", "weight": 0.25},
        {"region": "Europe", "tz": "Europe/London", "weight": 0.25},
        {"region": "Asia", "tz": "Asia/Kolkata", "weight": 0.15},
    ],
    "x": [
        {"region": "US", "tz": "US/Eastern", "weight": 0.40},
        {"region": "Europe", "tz": "Europe/London", "weight": 0.30},
        {"region": "Asia", "tz": "Asia/Tokyo", "weight": 0.15},
        {"region": "LATAM", "tz": "America/Sao_Paulo", "weight": 0.15},
    ],
    "instagram": [
        {"region": "US", "tz": "US/Eastern", "weight": 0.35},
        {"region": "Europe", "tz": "Europe/London", "weight": 0.25},
        {"region": "LATAM", "tz": "America/Sao_Paulo", "weight": 0.20},
        {"region": "Asia", "tz": "Asia/Kolkata", "weight": 0.20},
    ],
    "facebook": [
        {"region": "US", "tz": "US/Eastern", "weight": 0.30},
        {"region": "Europe", "tz": "Europe/London", "weight": 0.30},
        {"region": "Asia", "tz": "Asia/Kolkata", "weight": 0.20},
        {"region": "LATAM", "tz": "America/Sao_Paulo", "weight": 0.20},
    ],
    "youtube": [
        {"region": "US", "tz": "US/Pacific", "weight": 0.30},
        {"region": "India", "tz": "Asia/Kolkata", "weight": 0.25},
        {"region": "Europe", "tz": "Europe/Berlin", "weight": 0.20},
        {"region": "SE Asia", "tz": "Asia/Shanghai", "weight": 0.25},
    ],
}


def get_audience_timezones(platform: str) -> list[dict[str, Any]]:
    """Get likely audience timezones for a platform."""
    return AUDIENCE_TIMEZONES.get(platform, [])


def convert_to_audience_time(
    utc_datetime: datetime,
    target_tz: str,
) -> dict[str, Any]:
    """Convert a UTC datetime to an audience timezone.

    Returns the converted time and metadata.
    """
    try:
        import pytz
        target = pytz.timezone(target_tz)
        converted = utc_datetime.replace(tzinfo=timezone.utc).astimezone(target)
        return {
            "original_utc": utc_datetime.isoformat(),
            "converted": converted.isoformat(),
            "timezone": target_tz,
            "hour": converted.hour,
            "day_of_week": converted.strftime("%A"),
            "is_business_hours": 8 <= converted.hour <= 18,
        }
    except Exception:
        # Fallback without pytz
        return {
            "original_utc": utc_datetime.isoformat(),
            "timezone": target_tz,
            "note": "pytz not available for conversion",
        }


def suggest_audience_aware_time(
    platform: str,
    preferred_utc_hour: int = 10,
) -> list[dict[str, Any]]:
    """Suggest posting times that reach the most audience segments.

    For each audience timezone, calculate what UTC time corresponds to
    their peak hours, then find the UTC time that covers the most
    weighted audience.
    """
    audiences = get_audience_timezones(platform)
    if not audiences:
        return []

    suggestions = []
    for tz_info in audiences:
        tz_name = tz_info["tz"]
        weight = tz_info["weight"]
        region = tz_info["region"]

        # Convert preferred hour to each timezone
        try:
            import pytz
            tz = pytz.timezone(tz_name)
            # Target posting time in their timezone
            target_local = datetime.now(timezone.utc).replace(
                hour=preferred_utc_hour, minute=0, second=0, microsecond=0
            )
            # What UTC time is that in their timezone?
            target_utc = target_local.astimezone(timezone.utc)

            suggestions.append({
                "region": region,
                "timezone": tz_name,
                "weight": weight,
                "suggested_utc": target_utc.isoformat(),
                "local_time": f"{preferred_utc_hour}:00",
                "score": weight,
            })
        except Exception:
            pass

    # Sort by weight (reach most audience first)
    suggestions.sort(key=lambda x: x["score"], reverse=True)
    return suggestions


def get_best_utc_offset(
    platform: str,
    base_hour: int = 10,
) -> int:
    """Calculate the best UTC offset to post at for maximum audience reach.

    Returns the UTC hour that maximizes weighted audience coverage
    during their business hours.
    """
    audiences = get_audience_timezones(platform)
    if not audiences:
        return base_hour

    # Try each UTC hour and score it
    best_hour = base_hour
    best_score = 0

    for utc_hour in range(24):
        score = 0
        for tz_info in audiences:
            try:
                import pytz
                tz = pytz.timezone(tz_info["tz"])
                now = datetime.now(timezone.utc).replace(hour=utc_hour)
                local_time = now.astimezone(tz)
                # Score higher during business hours
                if 8 <= local_time.hour <= 18:
                    score += tz_info["weight"]
                elif 6 <= local_time.hour <= 20:
                    score += tz_info["weight"] * 0.5
            except Exception:
                score += tz_info["weight"] * 0.3

        if score > best_score:
            best_score = score
            best_hour = utc_hour

    return best_hour
