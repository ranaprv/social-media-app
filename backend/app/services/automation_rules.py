"""Automation rules engine — if-then scheduling automation.

Defines rules that automatically trigger actions based on conditions.
"""
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

# Built-in automation rules
AUTOMATION_RULES = [
    {
        "id": "rule-auto-recycle-top",
        "name": "Auto-recycle top performers",
        "description": "Automatically reschedule top-performing posts every 14 days",
        "trigger": {"type": "schedule", "interval_days": 14},
        "condition": {"engagement_rate_above": 5.0, "min_age_days": 14},
        "action": {"type": "recycle", "max_per_cycle": 2},
        "enabled": True,
    },
    {
        "id": "rule-notify-failed",
        "name": "Notify on failed publish",
        "description": "Send notification when a post fails to publish",
        "trigger": {"type": "event", "event": "publish_failed"},
        "condition": {},
        "action": {"type": "notify", "channel": "email"},
        "enabled": True,
    },
    {
        "id": "rule-auto-approve-drafts",
        "name": "Auto-approve drafts older than 48h",
        "description": "Move drafts to scheduled after 48 hours without changes",
        "trigger": {"type": "schedule", "interval_hours": 12},
        "condition": {"status": "draft", "age_hours_above": 48},
        "action": {"type": "transition", "to_status": "scheduled"},
        "enabled": False,
    },
    {
        "id": "rule-weekly-report",
        "name": "Weekly analytics report",
        "description": "Generate and send weekly analytics summary every Monday",
        "trigger": {"type": "cron", "day_of_week": 0, "hour": 9},
        "condition": {},
        "action": {"type": "report", "report_type": "weekly_summary"},
        "enabled": True,
    },
    {
        "id": "rule-token-refresh-alert",
        "name": "Token expiry alert",
        "description": "Alert when platform tokens are within 3 days of expiry",
        "trigger": {"type": "schedule", "interval_hours": 6},
        "condition": {"token_expiring_within_days": 3},
        "action": {"type": "notify", "channel": "email"},
        "enabled": True,
    },
]


def get_automation_rules() -> list[dict[str, Any]]:
    """Get all automation rules."""
    return AUTOMATION_RULES


def toggle_rule(rule_id: str, enabled: bool) -> dict[str, Any]:
    """Enable or disable an automation rule."""
    for rule in AUTOMATION_RULES:
        if rule["id"] == rule_id:
            rule["enabled"] = enabled
            return {"rule_id": rule_id, "enabled": enabled, "name": rule["name"]}
    return {"error": f"Rule {rule_id} not found"}


async def check_automation_triggers(db: Any, workspace_id: str) -> list[dict[str, Any]]:
    """Check if any automation rules should fire."""
    triggered: list[dict[str, Any]] = []

    for rule in AUTOMATION_RULES:
        if not rule["enabled"]:
            continue

        trigger = rule["trigger"]
        condition = rule["condition"]
        action = rule["action"]

        # Check trigger type
        if trigger["type"] == "event":
            # Event triggers are checked externally
            continue

        if trigger["type"] == "schedule" or trigger["type"] == "cron":
            # Schedule-based triggers need external scheduling (Celery beat)
            continue

    return triggered
