"""Content idea generator — AI brainstorm from keywords.

Generates content ideas based on keywords, industry, audience,
and trending topics.
"""
import logging
from typing import Any

from app.services.llm import call_llm_json

logger = logging.getLogger(__name__)


async def generate_content_ideas(
    keywords: list[str],
    industry: str = "technology",
    audience: str = "professionals",
    platforms: list[str] | None = None,
    count: int = 10,
    content_types: list[str] | None = None,
    provider: str = "openai",
) -> dict[str, Any]:
    """Generate content ideas based on keywords and parameters.

    Returns a list of content ideas with metadata.
    """
    target_platforms = platforms or ["linkedin", "x"]
    target_types = content_types or ["post", "thread", "carousel", "video"]

    system_prompt = (
        "You are an expert social media content strategist. "
        "Generate creative content ideas as JSON.\n\n"
        "Return a JSON array of ideas, each with:\n"
        '- "title": catchy title\n'
        '- "description": 1-2 sentence description\n'
        '- "platform": best platform for this idea\n'
        '- "content_type": post, thread, carousel, video, poll, story\n'
        '- "engagement_potential": high, medium, low\n'
        '- "keywords": relevant keywords\n'
        '- "hook": opening line or hook\n'
    )

    user_prompt = (
        f"Generate {count} content ideas.\n\n"
        f"Keywords: {', '.join(keywords)}\n"
        f"Industry: {industry}\n"
        f"Audience: {audience}\n"
        f"Platforms: {', '.join(target_platforms)}\n"
        f"Content types: {', '.join(target_types)}\n\n"
        "Make ideas:\n"
        "- Specific and actionable\n"
        "- Mix of educational, engaging, and promotional\n"
        "- Trend-aware and timely\n"
        "- Platform-native (not same idea everywhere)\n"
    )

    try:
        result = await call_llm_json(
            prompt=user_prompt,
            system_prompt=system_prompt,
            provider=provider,
            temperature=0.9,
            max_tokens=4000,
        )

        if result and isinstance(result, list):
            ideas = []
            for item in result:
                ideas.append({
                    "title": item.get("title", ""),
                    "description": item.get("description", ""),
                    "platform": item.get("platform", target_platforms[0]),
                    "content_type": item.get("content_type", "post"),
                    "engagement_potential": item.get("engagement_potential", "medium"),
                    "keywords": item.get("keywords", []),
                    "hook": item.get("hook", ""),
                })

            return {
                "ideas": ideas,
                "count": len(ideas),
                "keywords": keywords,
                "industry": industry,
                "audience": audience,
            }

    except Exception as e:
        logger.error(f"Idea generation failed: {e}")

    # Fallback: generate basic ideas from keywords
    fallback_ideas = []
    for kw in keywords[:count]:
        fallback_ideas.append({
            "title": f"10 Tips About {kw}",
            "description": f"Share expert tips about {kw} for {audience}",
            "platform": target_platforms[0],
            "content_type": "post",
            "engagement_potential": "medium",
            "keywords": [kw],
            "hook": f"Here are 10 things I wish I knew about {kw}...",
        })

    return {
        "ideas": fallback_ideas,
        "count": len(fallback_ideas),
        "keywords": keywords,
        "industry": industry,
        "audience": audience,
        "fallback": True,
    }


async def generate_trending_ideas(
    industry: str,
    platforms: list[str] | None = None,
    count: int = 5,
    provider: str = "openai",
) -> dict[str, Any]:
    """Generate ideas based on current trends."""
    system_prompt = (
        "You are a social media trend analyst. "
        "Generate content ideas based on current trending topics.\n"
        "Return JSON array with title, description, platform, content_type, trend_reason."
    )

    user_prompt = (
        f"Generate {count} trending content ideas for the {industry} industry.\n"
        f"Platforms: {', '.join(platforms or ['linkedin', 'x'])}\n"
        "Focus on:\n"
        "- Current hot topics in the industry\n"
        "- Timely and relevant content\n"
        "- High engagement potential\n"
    )

    try:
        result = await call_llm_json(
            prompt=user_prompt,
            system_prompt=system_prompt,
            provider=provider,
            temperature=0.9,
        )

        if result and isinstance(result, list):
            return {
                "ideas": result,
                "count": len(result),
                "industry": industry,
                "type": "trending",
            }

    except Exception as e:
        logger.error(f"Trending idea generation failed: {e}")

    return {"ideas": [], "count": 0, "industry": industry, "type": "trending"}
