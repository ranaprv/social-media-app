"""Content Brief Builder — structured briefs for content creation.

Guides users through creating comprehensive content briefs
with objectives, audience, tone, CTA, and success metrics.
"""
import logging
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Brief templates by content type
BRIEF_TEMPLATES = {
    "blog_post": {
        "name": "Blog Post Brief",
        "sections": ["objective", "target_audience", "key_message", "tone", "cta", "keywords", "success_metrics"],
        "required_fields": ["objective", "target_audience", "key_message"],
    },
    "social_post": {
        "name": "Social Media Post Brief",
        "sections": ["platform", "objective", "target_audience", "hook", "key_points", "cta", "hashtag_strategy"],
        "required_fields": ["platform", "objective", "hook"],
    },
    "video_script": {
        "name": "Video Script Brief",
        "sections": ["objective", "target_audience", "hook", "script_outline", "visual_cues", "cta", "length"],
        "required_fields": ["objective", "hook", "script_outline"],
    },
    "carousel": {
        "name": "Carousel Brief",
        "sections": ["objective", "slide_count", "slide_topics", "visual_style", "cta", "platform"],
        "required_fields": ["objective", "slide_count", "slide_topics"],
    },
    "newsletter": {
        "name": "Newsletter Brief",
        "sections": ["objective", "audience_segment", "topics", "tone", "cta", "send_time"],
        "required_fields": ["objective", "topics"],
    },
}


async def create_brief(
    db: AsyncSession,
    workspace_id: str,
    brief_type: str,
    title: str,
    content: dict[str, Any],
    platforms: list[str] | None = None,
) -> dict[str, Any]:
    """Create a structured content brief."""
    from app.models.content import Activity

    template = BRIEF_TEMPLATES.get(brief_type, BRIEF_TEMPLATES["social_post"])
    brief_id = str(uuid.uuid4())

    # Validate required fields
    missing = [f for f in template["required_fields"] if f not in content or not content.get(f)]
    if missing:
        return {"error": f"Missing required fields: {', '.join(missing)}"}

    activity = Activity(
        id=str(uuid.uuid4()),
        user_id="system",
        type="brief_created",
        description=f"Content brief created: {title}",
        meta={
            "brief_id": brief_id,
            "brief_type": brief_type,
            "title": title,
            "platforms": platforms or [],
        },
    )
    db.add(activity)
    await db.flush()

    return {
        "brief_id": brief_id,
        "type": brief_type,
        "title": title,
        "content": content,
        "platforms": platforms or [],
        "template": template,
        "status": "draft",
        "checklist": _generate_checklist(brief_type, content),
    }


def _generate_checklist(brief_type: str, content: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate a pre-creation checklist based on the brief."""
    checklist = [
        {"item": "Objective is clear and measurable", "checked": bool(content.get("objective"))},
        {"item": "Target audience defined", "checked": bool(content.get("target_audience"))},
        {"item": "Key message identified", "checked": bool(content.get("key_message") or content.get("hook"))},
        {"item": "Tone and voice specified", "checked": bool(content.get("tone"))},
        {"item": "Call-to-action defined", "checked": bool(content.get("cta"))},
    ]

    if brief_type == "social_post":
        checklist.append({"item": "Platform-specific formatting planned", "checked": False})
        checklist.append({"item": "Hashtag strategy defined", "checked": bool(content.get("hashtag_strategy"))})
    elif brief_type == "video_script":
        checklist.append({"item": "Script outline complete", "checked": bool(content.get("script_outline"))})
        checklist.append({"item": "Visual cues documented", "checked": bool(content.get("visual_cues"))})

    return checklist


def get_brief_templates() -> list[dict[str, Any]]:
    """Get available brief templates."""
    return [
        {"key": k, "name": v["name"], "sections": v["sections"], "required": v["required_fields"]}
        for k, v in BRIEF_TEMPLATES.items()
    ]
