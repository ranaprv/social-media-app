"""Influencer Discovery — find influencers by niche, audience size, engagement.

Provides influencer identification and outreach framework.
"""
import logging
from typing import Any

from app.services.llm import call_llm_json

logger = logging.getLogger(__name__)


async def discover_influencers(
    niche: str,
    platform: str = "instagram",
    min_followers: int = 1000,
    max_followers: int = 100000,
    min_engagement_rate: float = 2.0,
    count: int = 10,
    provider: str = "openai",
) -> dict[str, Any]:
    """Discover potential influencer partners.

    Uses AI to suggest influencer profiles based on niche criteria.
    """
    system_prompt = (
        "You are an influencer marketing expert. "
        "Suggest influencer profiles as JSON.\n\n"
        "Return a JSON array with:\n"
        '- "name": influencer name\n'
        '- "handle": social media handle\n'
        '- "platform": platform\n'
        '- "followers": estimated follower count\n'
        '- "engagement_rate": estimated engagement rate\n'
        '- "niche": their content niche\n'
        '- "content_style": description of their style\n'
        '- "fit_score": 0-100 how well they fit the criteria\n'
        '- "outreach_angle": suggested approach for collaboration'
    )

    user_prompt = (
        f"Find {count} influencer candidates for:\n"
        f"Niche: {niche}\n"
        f"Platform: {platform}\n"
        f"Followers: {min_followers:,} - {max_followers:,}\n"
        f"Min engagement rate: {min_engagement_rate}%\n"
    )

    try:
        result = await call_llm_json(
            prompt=user_prompt,
            system_prompt=system_prompt,
            provider=provider,
            temperature=0.7,
        )

        if result and isinstance(result, list):
            return {
                "influencers": result,
                "count": len(result),
                "criteria": {
                    "niche": niche,
                    "platform": platform,
                    "min_followers": min_followers,
                    "max_followers": max_followers,
                    "min_engagement_rate": min_engagement_rate,
                },
            }

    except Exception as e:
        logger.error(f"Influencer discovery failed: {e}")

    return {"influencers": [], "count": 0, "error": "Discovery failed"}


def get_outreach_templates() -> list[dict[str, str]]:
    """Get influencer outreach message templates."""
    return [
        {
            "name": "Cold Outreach",
            "template": "Hi {name}! We love your content about {topic}. We're {brand} and think our audience would benefit from a collaboration. Would you be open to discussing a partnership?",
        },
        {
            "name": "Warm Introduction",
            "template": "Hey {name}! {mutual_connection} suggested I reach out. We're huge fans of your {platform} content. Would love to explore a collaboration that benefits both our audiences.",
        },
        {
            "name": "Value-First",
            "template": "Hi {name}! We created something we think your audience would love: {offer}. Want to try it and share your honest thoughts?",
        },
        {
            "name": "Event Invite",
            "template": "Hi {name}! We're hosting {event} and would love to have you involved. It's a great opportunity to connect with {audience}. Interested?",
        },
    ]


def get_influencer_vetting_checklist() -> list[dict[str, str]]:
    """Get checklist for vetting potential influencer partners."""
    return [
        {"check": "Engagement rate above 2%", "why": "Low engagement = fake followers or inactive audience"},
        {"check": "Audience demographics match target", "why": "Wrong audience = wasted spend"},
        {"check": "Content quality is consistent", "why": "Inconsistent quality = unreliable partner"},
        {"check": "No controversial history", "why": "Brand safety risk"},
        {"check": "Previous brand collaborations", "why": "Experience = smoother execution"},
        {"check": "Response time to DMs", "why": "Slow responders = difficult to work with"},
        {"check": "Follower growth is organic", "why": "Sudden spikes = purchased followers"},
        {"check": "Content aligns with brand values", "why": "Misalignment = audience backlash"},
    ]
