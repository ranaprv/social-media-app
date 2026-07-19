"""Workspace settings — platform defaults, timezone, posting preferences.

Manages workspace-level scheduling configuration.
"""
import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workspace import Workspace

logger = logging.getLogger(__name__)

# Default workspace settings
DEFAULT_SETTINGS = {
    "timezone": "US/Eastern",
    "auto_publish": False,
    "queue_enabled": True,
    "max_daily_posts": 10,
    "default_platforms": ["linkedin", "x"],
    "posting_hours": {"start": 8, "end": 20},
    "notification_channels": [],
    "brand_voice_id": None,
    "auto_shorten_links": True,
    "auto_add_utm": True,
    "utm_campaign_prefix": "smm",
    "content_approval_required": False,
    "recycle_enabled": True,
    "recycle_max_per_week": 2,
    "recycle_min_age_days": 14,
}


async def get_workspace_settings(
    db: AsyncSession,
    workspace_id: str,
) -> dict[str, Any]:
    """Get workspace scheduling settings."""
    result = await db.execute(
        select(Workspace).where(Workspace.id == workspace_id)
    )
    workspace = result.scalar_one_none()

    if workspace:
        meta = workspace.meta or {}
        settings = {**DEFAULT_SETTINGS, **meta.get("scheduler_settings", {})}
    else:
        settings = dict(DEFAULT_SETTINGS)

    return {
        "workspace_id": workspace_id,
        "settings": settings,
    }


async def update_workspace_settings(
    db: AsyncSession,
    workspace_id: str,
    updates: dict[str, Any],
) -> dict[str, Any]:
    """Update workspace scheduling settings."""
    result = await db.execute(
        select(Workspace).where(Workspace.id == workspace_id)
    )
    workspace = result.scalar_one_none()

    if not workspace:
        return {"error": f"Workspace {workspace_id} not found"}

    meta = workspace.meta or {}
    current_settings = {**DEFAULT_SETTINGS, **meta.get("scheduler_settings", {})}

    # Apply updates (only known keys)
    for key, value in updates.items():
        if key in DEFAULT_SETTINGS:
            current_settings[key] = value

    meta["scheduler_settings"] = current_settings
    workspace.meta = meta

    await db.flush()

    return {
        "workspace_id": workspace_id,
        "settings": current_settings,
        "message": "Settings updated",
    }


def get_settings_schema() -> list[dict[str, Any]]:
    """Get the settings schema for UI rendering."""
    return [
        {"key": "timezone", "type": "select", "label": "Default Timezone", "options": [
            "UTC", "US/Eastern", "US/Central", "US/Pacific", "Europe/London",
            "Europe/Paris", "Europe/Berlin", "Asia/Tokyo", "Asia/Shanghai",
            "Asia/Kolkata", "Australia/Sydney",
        ]},
        {"key": "auto_publish", "type": "boolean", "label": "Auto-publish scheduled posts"},
        {"key": "queue_enabled", "type": "boolean", "label": "Enable publishing queue"},
        {"key": "max_daily_posts", "type": "number", "label": "Max posts per day", "min": 1, "max": 100},
        {"key": "default_platforms", "type": "multi_select", "label": "Default platforms", "options": [
            "linkedin", "x", "instagram", "facebook", "youtube",
        ]},
        {"key": "posting_hours_start", "type": "number", "label": "Posting hours start (0-23)", "min": 0, "max": 23},
        {"key": "posting_hours_end", "type": "number", "label": "Posting hours end (0-23)", "min": 0, "max": 23},
        {"key": "auto_shorten_links", "type": "boolean", "label": "Auto-shorten links"},
        {"key": "auto_add_utm", "type": "boolean", "label": "Auto-add UTM parameters"},
        {"key": "utm_campaign_prefix", "type": "text", "label": "UTM campaign prefix"},
        {"key": "content_approval_required", "type": "boolean", "label": "Require approval before publishing"},
        {"key": "recycle_enabled", "type": "boolean", "label": "Enable content recycling"},
        {"key": "recycle_max_per_week", "type": "number", "label": "Max recycles per week", "min": 0, "max": 10},
        {"key": "recycle_min_age_days", "type": "number", "label": "Min age before recycling (days)", "min": 1, "max": 90},
    ]
