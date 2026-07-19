"""Smart scheduling rules — auto-schedule based on rules.

Defines configurable rules that automatically schedule posts
based on content type, platform, audience, and optimal times.
"""
import logging
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)

# Predefined smart scheduling rules
SMART_RULES = [
    {
        "id": "rule-optimal-time",
        "name": "Schedule at Optimal Time",
        "description": "Automatically schedule posts at the best time for each platform based on historical engagement",
        "enabled": True,
        "priority": 1,
        "conditions": {"always": True},
        "action": "schedule_at_best_time",
    },
    {
        "id": "rule-avoid-conflicts",
        "name": "Avoid Scheduling Conflicts",
        "description": "Don't schedule two posts to the same platform within 2 hours of each other",
        "enabled": True,
        "priority": 2,
        "conditions": {"min_gap_hours": 2},
        "action": "avoid_conflicts",
    },
    {
        "id": "rule-respect-hours",
        "name": "Respect Business Hours",
        "description": "Only schedule posts between 8 AM and 10 PM in the audience timezone",
        "enabled": True,
        "priority": 3,
        "conditions": {"start_hour": 8, "end_hour": 22},
        "action": "respect_hours",
    },
    {
        "id": "rule-balance-platforms",
        "name": "Balance Platform Distribution",
        "description": "Don't post to the same platform more than 3 times per day",
        "enabled": True,
        "priority": 4,
        "conditions": {"max_per_day": 3},
        "action": "balance_distribution",
    },
    {
        "id": "rule-queue-cap",
        "name": "Queue Capacity Limit",
        "description": "Don't exceed 20 scheduled posts in the queue at once",
        "enabled": True,
        "priority": 5,
        "conditions": {"max_queue_size": 20},
        "action": "cap_queue",
    },
    {
        "id": "rule-weekend-adjust",
        "name": "Weekend Adjustment",
        "description": "Shift weekend posts 2 hours later (audiences sleep in)",
        "enabled": False,
        "priority": 6,
        "conditions": {"weekend_offset_hours": 2},
        "action": "adjust_weekend",
    },
]


async def apply_smart_rules(
    requested_time: datetime,
    platform: str,
    workspace_id: str,
    db: Any,
    existing_schedule: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Apply smart scheduling rules to find the best time.

    Takes a requested time and adjusts it based on enabled rules.
    """
    adjusted_time = requested_time
    applied_rules: list[str] = []
    adjustments: list[dict[str, Any]] = []

    for rule in SMART_RULES:
        if not rule["enabled"]:
            continue

        action = rule["action"]
        conditions = rule["conditions"]

        if action == "respect_hours":
            start = conditions.get("start_hour", 8)
            end = conditions.get("end_hour", 22)
            if adjusted_time.hour < start:
                adjusted_time = adjusted_time.replace(hour=start, minute=0)
                adjustments.append({"rule": rule["id"], "adjustment": f"Moved to {start}:00 (business hours)"})
                applied_rules.append(rule["id"])
            elif adjusted_time.hour >= end:
                adjusted_time = adjusted_time.replace(hour=end - 1, minute=0)
                adjustments.append({"rule": rule["id"], "adjustment": f"Moved to {end-1}:00 (business hours)"})
                applied_rules.append(rule["id"])

        elif action == "adjust_weekend":
            if adjusted_time.weekday() >= 5:  # Saturday or Sunday
                offset = conditions.get("weekend_offset_hours", 2)
                adjusted_time += timedelta(hours=offset)
                adjustments.append({"rule": rule["id"], "adjustment": f"Shifted +{offset}h for weekend"})
                applied_rules.append(rule["id"])

        elif action == "avoid_conflicts" and existing_schedule:
            min_gap = conditions.get("min_gap_hours", 2)
            for existing in existing_schedule:
                if existing.get("platform") == platform:
                    try:
                        exist_time = datetime.fromisoformat(existing["scheduled_at"])
                        diff = abs((adjusted_time - exist_time).total_seconds() / 3600)
                        if diff < min_gap:
                            # Move to after the existing post
                            adjusted_time = exist_time + timedelta(hours=min_gap)
                            adjustments.append({
                                "rule": rule["id"],
                                "adjustment": f"Moved to avoid conflict (min {min_gap}h gap)",
                            })
                            applied_rules.append(rule["id"])
                            break
                    except (ValueError, KeyError):
                        pass

    return {
        "original_time": requested_time.isoformat(),
        "adjusted_time": adjusted_time.isoformat(),
        "was_adjusted": adjusted_time != requested_time,
        "applied_rules": applied_rules,
        "adjustments": adjustments,
    }


def get_smart_rules() -> list[dict[str, Any]]:
    """Get all smart scheduling rules."""
    return SMART_RULES


def update_rule(rule_id: str, enabled: bool | None = None, **kwargs) -> dict[str, Any]:
    """Update a smart scheduling rule."""
    for rule in SMART_RULES:
        if rule["id"] == rule_id:
            if enabled is not None:
                rule["enabled"] = enabled
            for key, value in kwargs.items():
                if key in rule["conditions"]:
                    rule["conditions"][key] = value
            return {"rule_id": rule_id, "updated": True, "rule": rule}
    return {"error": f"Rule {rule_id} not found"}
