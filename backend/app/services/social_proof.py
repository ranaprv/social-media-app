"""Social Proof Aggregator — testimonials, reviews, UGC showcase.

Collects and organizes social proof for marketing use.
"""
import logging
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def get_social_proof(
    db: AsyncSession,
    workspace_id: str,
    category: str | None = None,
    platform: str | None = None,
) -> dict[str, Any]:
    """Get aggregated social proof content."""
    # In production, this would query a social_proof table
    # For now, return structure with sample data
    return {
        "testimonials": [],
        "reviews": [],
        "ugc_highlights": [],
        "metrics": {
            "total_testimonials": 0,
            "average_rating": 0,
            "nps_score": 0,
            "ugc_submissions": 0,
        },
        "categories": ["testimonial", "review", "ugc", "press", "award"],
    }


async def add_social_proof(
    db: AsyncSession,
    workspace_id: str,
    category: str,
    content: str,
    author: str = "",
    platform: str = "",
    rating: int | None = None,
    url: str = "",
) -> dict[str, Any]:
    """Add a social proof entry."""
    from app.models.content import Activity

    proof_id = str(uuid.uuid4())
    activity = Activity(
        id=str(uuid.uuid4()),
        user_id="system",
        type="social_proof_added",
        description=f"Social proof added: {category}",
        meta={
            "proof_id": proof_id,
            "category": category,
            "author": author,
            "platform": platform,
        },
    )
    db.add(activity)
    await db.flush()

    return {
        "proof_id": proof_id,
        "category": category,
        "content_preview": content[:100],
        "author": author,
    }


def get_social_proof_templates() -> list[dict[str, str]]:
    """Get templates for requesting social proof."""
    return [
        {"name": "Testimonial Request", "template": "Hi {name}! We'd love to feature your experience with {product}. Would you mind sharing a short testimonial about how it's helped you?"},
        {"name": "Review Request", "template": "Thanks for using {product}! If you have a moment, we'd appreciate a review on {platform}. It helps other {audience} discover us."},
        {"name": "Case Study Invitation", "template": "Hi {name}, we noticed {result} using {product}. Would you be open to a short case study featuring your success story?"},
        {"name": "UGC Campaign", "template": "Share how you use {product} with #{hashtag} for a chance to be featured on our page!"},
    ]
