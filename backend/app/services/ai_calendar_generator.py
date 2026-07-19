"""AI Calendar Generator — auto-generate full month content plans.

Uses LLM to create a complete content calendar based on topic,
audience, platforms, and posting frequency.
"""
import logging
from typing import Any

from app.services.llm import call_llm_json

logger = logging.getLogger(__name__)


async def generate_monthly_calendar(
    topic: str,
    platforms: list[str],
    audience: str = "general",
    posting_frequency: str = "daily",
    brand_voice: str | None = None,
    content_pillars: list[str] | None = None,
    month: int | None = None,
    year: int | None = None,
    provider: str = "openai",
) -> dict[str, Any]:
    """Generate a complete monthly content calendar.

    Returns a structured calendar with daily posts for each platform.
    """
    from datetime import datetime
    now = datetime.utcnow()
    target_month = month or now.month
    target_year = year or now.year

    system_prompt = (
        "You are an expert social media content strategist. "
        "Generate a complete monthly content calendar as JSON.\n\n"
        "Return a JSON object with this structure:\n"
        '{\n'
        '  "calendar": [\n'
        '    {\n'
        '      "day": 1,\n'
        '      "weekday": "Monday",\n'
        '      "posts": [\n'
        '        {\n'
        '          "platform": "linkedin",\n'
        '          "content_type": "text",\n'
        '          "title": "Post title",\n'
        '          "content": "Post content (200-300 chars)",\n'
        '          "best_time": "09:00",\n'
        '          "pillar": "educational",\n'
        '          "hashtags": ["#tag1", "#tag2"],\n'
        '          "cta": "What do you think?"\n'
        '        }\n'
        '      ]\n'
        '    }\n'
        '  ],\n'
        '  "content_mix": {\n'
        '    "educational": 30,\n'
        '    "engagement": 25,\n'
        '    "promotional": 15,\n'
        '    "behind_scenes": 15,\n'
        '    "curated": 15\n'
        '  },\n'
        '  "themes_by_week": ["Week 1 theme", ...]\n'
        '}'
    )

    user_prompt = (
        f"Generate a content calendar for {target_month}/{target_year}.\n\n"
        f"Topic: {topic}\n"
        f"Platforms: {', '.join(platforms)}\n"
        f"Audience: {audience}\n"
        f"Posting frequency: {posting_frequency}\n"
    )

    if brand_voice:
        user_prompt += f"Brand voice: {brand_voice}\n"
    if content_pillars:
        user_prompt += f"Content pillars: {', '.join(content_pillars)}\n"

    user_prompt += (
        "\nEnsure:\n"
        "- Mix content types (text, image, video, carousel, poll)\n"
        "- Vary posting times across the week\n"
        "- Include weekends (lighter posting)\n"
        "- Platform-native content (not same post everywhere)\n"
        "- At least 30 days of content\n"
    )

    try:
        result = await call_llm_json(
            prompt=user_prompt,
            system_prompt=system_prompt,
            provider=provider,
            temperature=0.8,
            max_tokens=8000,
        )

        if result and isinstance(result, dict):
            calendar = result.get("calendar", [])
            total_posts = sum(len(day.get("posts", [])) for day in calendar)

            return {
                "calendar": calendar,
                "month": target_month,
                "year": target_year,
                "total_days": len(calendar),
                "total_posts": total_posts,
                "content_mix": result.get("content_mix", {}),
                "themes_by_week": result.get("themes_by_week", []),
                "platforms": platforms,
                "topic": topic,
            }

    except Exception as e:
        logger.error(f"Calendar generation failed: {e}")

    # Fallback: simple calendar
    return _generate_fallback_calendar(target_month, target_year, platforms, topic)


def _generate_fallback_calendar(
    month: int, year: int, platforms: list[str], topic: str
) -> dict[str, Any]:
    """Generate a basic fallback calendar."""
    from datetime import datetime, timedelta
    import calendar

    days_in_month = calendar.monthrange(year, month)[1]
    days = []
    content_types = ["text", "image", "video", "poll", "carousel"]

    for day in range(1, days_in_month + 1):
        dt = datetime(year, month, day)
        posts = []
        for i, platform in enumerate(platforms[:2]):  # Max 2 platforms per day
            posts.append({
                "platform": platform,
                "content_type": content_types[day % len(content_types)],
                "title": f"{topic} - Day {day}",
                "content": f"Content about {topic} for {platform}",
                "best_time": "09:00" if i == 0 else "14:00",
                "pillar": "educational",
                "hashtags": [],
                "cta": "",
            })

        days.append({
            "day": day,
            "weekday": dt.strftime("%A"),
            "posts": posts,
        })

    return {
        "calendar": days,
        "month": month,
        "year": year,
        "total_days": days_in_month,
        "total_posts": sum(len(d["posts"]) for d in days),
        "content_mix": {},
        "themes_by_week": [],
        "platforms": platforms,
        "topic": topic,
        "fallback": True,
    }
