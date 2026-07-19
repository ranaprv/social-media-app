"""Hashtag strategist — AI-powered hashtag research per platform.

Generates optimal hashtags based on topic, platform, and trending data.
"""
import logging
from typing import Any

from app.services.llm import call_llm, call_llm_json

logger = logging.getLogger(__name__)

HASHTAG_SYSTEM_PROMPTS = {
    "linkedin": (
        "You are a LinkedIn hashtag strategist. Generate hashtags for LinkedIn posts.\n"
        "Rules:\n"
        "- Use 3-5 hashtags max (LinkedIn penalizes hashtag spam)\n"
        "- Mix broad and niche hashtags\n"
        "- Use title case: #ContentMarketing not #contentmarketing\n"
        "- Avoid overly generic tags like #business or #marketing\n"
        "- Focus on industry-specific and topic-specific tags"
    ),
    "x": (
        "You are an X/Twitter hashtag strategist.\n"
        "Rules:\n"
        "- Use 1-2 hashtags max (X penalizes hashtag-heavy tweets)\n"
        "- Hashtags should feel natural, not forced\n"
        "- Use trending or niche tags relevant to the topic\n"
        "- Lowercase: #socialmedia not #SocialMedia"
    ),
    "instagram": (
        "You are an Instagram hashtag strategist.\n"
        "Rules:\n"
        "- Use 5-10 hashtags (sweet spot for engagement)\n"
        "- Mix: 2-3 niche (<50k posts), 2-3 mid (50k-500k), 1-2 broad (500k+)\n"
        "- Place hashtags at the end of the caption or in first comment\n"
        "- Use lowercase: #socialmediamarketing\n"
        "- Rotate hashtags to avoid shadowban"
    ),
    "facebook": (
        "You are a Facebook hashtag strategist.\n"
        "Rules:\n"
        "- Use 1-3 hashtags max (Facebook hashtags have minimal impact)\n"
        "- Focus on brand and campaign hashtags\n"
        "- Keep them short and memorable"
    ),
    "youtube": (
        "You are a YouTube hashtag strategist.\n"
        "Rules:\n"
        "- Use 3-5 hashtags in the description\n"
        "- First 3 hashtags appear above the title\n"
        "- Include one broad discovery tag\n"
        "- Mix with niche topic tags\n"
        "- Use title case for readability"
    ),
}


async def generate_hashtags(
    topic: str,
    platform: str,
    content: str | None = None,
    count: int = 5,
    brand_hashtags: list[str] | None = None,
    provider: str = "openai",
) -> dict[str, Any]:
    """Generate optimized hashtags for a platform.

    Returns hashtags with metadata about each one.
    """
    system_prompt = HASHTAG_SYSTEM_PROMPTS.get(platform, HASHTAG_SYSTEM_PROMPTS["linkedin"])

    user_prompt = f"Generate {count} hashtags for this topic on {platform}:\n\nTopic: {topic}\n"
    if content:
        user_prompt += f"Content: {content[:500]}\n"
    if brand_hashtags:
        user_prompt += f"Brand hashtags to include: {', '.join(brand_hashtags)}\n"

    user_prompt += (
        f"\nReturn as JSON array: [{{\"tag\": \"#Hashtag\", \"category\": \"niche|mid|broad\", "
        f"\"estimated_reach\": \"high|medium|low\", \"relevance\": \"high|medium|low\"}}]"
    )

    try:
        result = await call_llm_json(
            prompt=user_prompt,
            system_prompt=system_prompt,
            provider=provider,
            temperature=0.7,
        )

        if result and isinstance(result, list):
            hashtags = []
            for item in result:
                tag = item.get("tag", "")
                if not tag.startswith("#"):
                    tag = f"#{tag}"
                hashtags.append({
                    "tag": tag,
                    "category": item.get("category", "niche"),
                    "estimated_reach": item.get("estimated_reach", "medium"),
                    "relevance": item.get("relevance", "high"),
                })

            # Ensure brand hashtags are included
            if brand_hashtags:
                existing_tags = {h["tag"].lower() for h in hashtags}
                for bh in brand_hashtags:
                    tag = bh if bh.startswith("#") else f"#{bh}"
                    if tag.lower() not in existing_tags:
                        hashtags.append({
                            "tag": tag,
                            "category": "brand",
                            "estimated_reach": "medium",
                            "relevance": "high",
                        })

            return {
                "hashtags": hashtags,
                "count": len(hashtags),
                "platform": platform,
                "topic": topic,
            }

    except Exception as e:
        logger.error(f"Hashtag generation failed: {e}")

    # Fallback: basic hashtags from topic
    words = topic.lower().split()
    fallback_tags = [f"#{word}" for word in words[:3] if len(word) > 3]
    return {
        "hashtags": [{"tag": t, "category": "fallback", "estimated_reach": "low", "relevance": "medium"} for t in fallback_tags],
        "count": len(fallback_tags),
        "platform": platform,
        "topic": topic,
        "fallback": True,
    }


async def analyze_hashtag_performance(
    content: str,
    platform: str,
) -> dict[str, Any]:
    """Analyze existing hashtags in content and suggest improvements."""
    import re
    existing = re.findall(r"#\w+", content)

    # Basic analysis
    analysis = {
        "existing_count": len(existing),
        "existing_tags": existing,
        "issues": [],
        "suggestions": [],
    }

    # Platform-specific checks
    limits = {
        "linkedin": {"optimal": (3, 5), "max": 5},
        "x": {"optimal": (1, 2), "max": 3},
        "instagram": {"optimal": (5, 10), "max": 30},
        "facebook": {"optimal": (1, 3), "max": 5},
        "youtube": {"optimal": (3, 5), "max": 15},
    }

    platform_limits = limits.get(platform, {"optimal": (3, 5), "max": 10})
    opt_min, opt_max = platform_limits["optimal"]

    if len(existing) < opt_min:
        analysis["issues"].append(f"Too few hashtags ({len(existing)}). Optimal: {opt_min}-{opt_max}")
        analysis["suggestions"].append(f"Add {opt_min - len(existing)} more relevant hashtags")
    elif len(existing) > platform_limits["max"]:
        analysis["issues"].append(f"Too many hashtags ({len(existing)}). Max: {platform_limits['max']}")
        analysis["suggestions"].append("Reduce hashtag count to avoid penalties")

    # Check for generic hashtags
    generic = {"#business", "#marketing", "#social", "#love", "#instagood", "#photooftheday"}
    found_generic = [t for t in existing if t.lower() in generic]
    if found_generic:
        analysis["issues"].append(f"Generic hashtags found: {', '.join(found_generic)}")
        analysis["suggestions"].append("Replace generic hashtags with niche-specific ones")

    analysis["score"] = max(0, 100 - len(analysis["issues"]) * 20)

    return analysis
