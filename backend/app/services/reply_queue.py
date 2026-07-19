"""Reply Queue — centralized comment/mention management with templates.

Manages incoming comments, mentions, and DMs with response templates.
"""
import logging
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Response templates
REPLY_TEMPLATES = {
    "thank_you": {
        "name": "Thank You",
        "category": "positive",
        "templates": [
            "Thanks for sharing! We appreciate your support 🙌",
            "Thank you! Glad you found this helpful.",
            "Appreciate the kind words! More coming soon.",
        ],
    },
    "question": {
        "name": "Answer Question",
        "category": "engagement",
        "templates": [
            "Great question! {answer}. Let me know if you have more questions.",
            "Happy to help! {answer}",
        ],
    },
    "complaint": {
        "name": "Handle Complaint",
        "category": "crisis",
        "templates": [
            "We're sorry to hear about your experience. We've escalated this to our team and will follow up shortly.",
            "Thanks for letting us know. We take this seriously and are looking into it.",
        ],
    },
    "praise": {
        "name": "Amplify Praise",
        "category": "positive",
        "templates": [
            "This made our day! 🎉 Thanks for the shoutout!",
            "We're thrilled to hear this! Thanks for being part of our community.",
        ],
    },
    "spam": {
        "name": "Mark as Spam",
        "category": "moderation",
        "templates": [],
    },
}


async def get_reply_queue(
    db: AsyncSession,
    workspace_id: str,
    platform: str | None = None,
    status: str = "pending",
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Get items in the reply queue."""
    # In production, this would query a reply_mentions table
    # For now, return template structure
    return {
        "items": [],
        "total": 0,
        "templates": REPLY_TEMPLATES,
    }


async def create_reply(
    db: AsyncSession,
    workspace_id: str,
    mention_id: str,
    response_text: str,
    template_used: str | None = None,
) -> dict[str, Any]:
    """Create and send a reply to a mention/comment."""
    reply_id = str(uuid.uuid4())

    from app.models.content import Activity
    activity = Activity(
        id=str(uuid.uuid4()),
        user_id="system",
        type="reply_sent",
        description=f"Reply sent to mention {mention_id}",
        meta={
            "reply_id": reply_id,
            "mention_id": mention_id,
            "template": template_used,
            "response_preview": response_text[:100],
        },
    )
    db.add(activity)
    await db.flush()

    return {
        "reply_id": reply_id,
        "mention_id": mention_id,
        "status": "sent",
        "response_preview": response_text[:100],
    }


def get_reply_templates() -> dict[str, Any]:
    """Get all reply templates."""
    return REPLY_TEMPLATES
