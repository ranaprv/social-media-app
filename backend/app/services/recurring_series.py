"""Recurring post series — create schedule patterns for recurring content.

Supports daily, weekly, and monthly recurrence with platform-specific
content variations (e.g. weekly thread, daily tip).
"""
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post
from app.models.post_platform import PostPlatform

logger = logging.getLogger(__name__)


# Predefined recurring series templates
RECURRING_TEMPLATES: dict[str, dict[str, Any]] = {
    "weekly_thread": {
        "name": "Weekly Thread",
        "description": "A weekly thread/post on a rotating topic",
        "frequency": "weekly",
        "default_platforms": ["x", "linkedin"],
        "default_day": 1,  # Tuesday
        "default_hour": 9,
        "content_template": "🧵 Weekly Thread: {topic}\n\n{content}\n\nWhat do you think? Drop your thoughts below 👇",
    },
    "daily_tip": {
        "name": "Daily Tip",
        "description": "A daily quick tip for your audience",
        "frequency": "daily",
        "default_platforms": ["linkedin", "x"],
        "default_hour": 8,
        "content_template": "💡 Daily Tip: {topic}\n\n{content}\n\n#TipOfTheDay",
    },
    "weekly_recap": {
        "name": "Weekly Recap",
        "description": "End-of-week summary of key events",
        "frequency": "weekly",
        "default_platforms": ["linkedin", "facebook"],
        "default_day": 4,  # Friday
        "default_hour": 15,
        "content_template": "📰 Weekly Recap — {date_range}\n\n{content}\n\nHave a great weekend! 🎉",
    },
    "monthly_newsletter": {
        "name": "Monthly Newsletter",
        "description": "Monthly newsletter-style post",
        "frequency": "monthly",
        "default_platforms": ["linkedin", "facebook"],
        "default_day": 1,
        "default_hour": 10,
        "content_template": "📬 Monthly Update — {month}\n\n{content}\n\nStay tuned for more next month!",
    },
    "monday_motivation": {
        "name": "Monday Motivation",
        "description": "Start the week with motivational content",
        "frequency": "weekly",
        "default_platforms": ["instagram", "linkedin"],
        "default_day": 0,  # Monday
        "default_hour": 9,
        "content_template": "💪 Monday Motivation\n\n{content}\n\nWhat's your goal this week? Drop it below! 👇",
    },
}


async def create_recurring_series(
    db: AsyncSession,
    workspace_id: str,
    template_key: str,
    content_items: list[dict[str, str]],
    start_date: datetime,
    platforms: list[str] | None = None,
    custom_template: str | None = None,
) -> dict[str, Any]:
    """Create a recurring series of scheduled posts.

    Args:
        template_key: Key from RECURRING_TEMPLATES (e.g. "weekly_thread").
        content_items: List of content dicts with "topic" and "content" keys.
        start_date: When to start the series.
        platforms: Override default platforms.
        custom_template: Override the content template.

    Returns:
        Summary of created posts.
    """
    template = RECURRING_TEMPLATES.get(template_key)
    if not template:
        return {"error": f"Unknown template: {template_key}"}

    frequency = template["frequency"]
    target_platforms = platforms or template["default_platforms"]
    content_template = custom_template or template["content_template"]

    created = []
    current_date = start_date

    for i, item in enumerate(content_items):
        topic = item.get("topic", f"Topic {i + 1}")
        content = item.get("content", "")

        # Format the content
        formatted_content = content_template.format(
            topic=topic,
            content=content,
            date_range=f"{current_date.strftime('%b %d')} - {(current_date + timedelta(days=6)).strftime('%b %d')}",
            month=current_date.strftime("%B %Y"),
        )

        # Create the Post
        post = Post(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            author_id="system",  # System-generated
            title=topic,
            content=formatted_content,
            platform=target_platforms[0],
            status="scheduled",
            scheduled_at=current_date,
            meta={"recurring_series": template_key, "series_index": i},
        )
        db.add(post)

        # Create PostPlatform entries for each platform
        for platform in target_platforms:
            pp = PostPlatform(
                id=str(uuid.uuid4()),
                post_id=post.id,
                workspace_id=workspace_id,
                platform=platform,
                status="scheduled",
                scheduled_at=current_date,
            )
            db.add(pp)
            created.append({
                "post_id": post.id,
                "platform": platform,
                "scheduled_at": current_date.isoformat(),
                "topic": topic,
            })

        # Advance date based on frequency
        if frequency == "daily":
            current_date += timedelta(days=1)
        elif frequency == "weekly":
            current_date += timedelta(weeks=1)
        elif frequency == "monthly":
            # Move to same day next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)

    await db.flush()

    return {
        "series": template_key,
        "frequency": frequency,
        "platforms": target_platforms,
        "total_posts": len(content_items),
        "created_entries": len(created),
        "date_range": {
            "start": start_date.isoformat(),
            "end": (current_date - timedelta(days=1)).isoformat(),
        },
        "items": created,
    }


def get_recurring_templates() -> list[dict[str, Any]]:
    """List all available recurring series templates."""
    return [
        {
            "key": key,
            "name": tmpl["name"],
            "description": tmpl["description"],
            "frequency": tmpl["frequency"],
            "default_platforms": tmpl["default_platforms"],
            "default_day": tmpl.get("default_day"),
            "default_hour": tmpl.get("default_hour"),
        }
        for key, tmpl in RECURRING_TEMPLATES.items()
    ]
