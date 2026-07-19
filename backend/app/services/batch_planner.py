"""Content Batch Planner — weekly/monthly batch creation with scheduling.

Plans content batches with platform-specific scheduling.
"""
import logging
from datetime import datetime, timedelta
from typing import Any

from app.services.llm import call_llm_json

logger = logging.getLogger(__name__)


async def plan_weekly_batch(
    topic: str,
    platforms: list[str],
    pillars: list[str] | None = None,
    brand_voice: str | None = None,
    provider: str = "openai",
) -> dict[str, Any]:
    """Plan a week of content across platforms."""
    target_pillars = pillars or ["educational", "engagement", "promotional"]

    system_prompt = (
        "You are a content strategist planning a weekly content batch.\n"
        "Generate a 7-day content plan as JSON.\n\n"
        "Return:\n"
        '{\n'
        '  "week_start": "2026-07-21",\n'
        '  "days": [\n'
        '    {\n'
        '      "day": "Monday",\n'
        '      "date": "2026-07-21",\n'
        '      "posts": [\n'
        '        {\n'
        '          "platform": "linkedin",\n'
        '          "pillar": "educational",\n'
        '          "content_type": "post",\n'
        '          "topic": "...",\n'
        '          "hook": "...",\n'
        '          "best_time": "09:00"\n'
        '        }\n'
        '      ]\n'
        '    }\n'
        '  ],\n'
        '  "content_mix": {"educational": 30, "engagement": 25, "promotional": 15, ...}\n'
        '}'
    )

    user_prompt = (
        f"Plan a weekly content batch for:\n"
        f"Topic: {topic}\n"
        f"Platforms: {', '.join(platforms)}\n"
        f"Pillars: {', '.join(target_pillars)}\n"
    )
    if brand_voice:
        user_prompt += f"Brand voice: {brand_voice}\n"

    try:
        result = await call_llm_json(
            prompt=user_prompt,
            system_prompt=system_prompt,
            provider=provider,
            temperature=0.8,
            max_tokens=4000,
        )

        if result and isinstance(result, dict):
            days = result.get("days", [])
            total_posts = sum(len(d.get("posts", [])) for d in days)
            return {
                "plan": result,
                "total_days": len(days),
                "total_posts": total_posts,
                "platforms": platforms,
                "topic": topic,
            }

    except Exception as e:
        logger.error(f"Batch planning failed: {e}")

    return {"plan": None, "error": "Planning failed"}


async def plan_monthly_batch(
    topic: str,
    platforms: list[str],
    pillars: list[str] | None = None,
    provider: str = "openai",
) -> dict[str, Any]:
    """Plan a month of content (4 weekly batches)."""
    weeks = []
    for week in range(4):
        week_plan = await plan_weekly_batch(topic, platforms, pillars, provider=provider)
        weeks.append(week_plan)

    return {
        "weeks": weeks,
        "total_weeks": len(weeks),
        "platforms": platforms,
        "topic": topic,
    }
