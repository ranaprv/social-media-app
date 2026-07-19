"""Content Repurposing Engine — turn one piece into many formats.

Transforms a blog post, article, or video script into multiple
platform-native content formats.
"""
import logging
from typing import Any

from app.services.llm import call_llm_json

logger = logging.getLogger(__name__)

# Repurposing transformation rules
REPURPOSE_ROUTES = {
    "blog_to_thread": {
        "name": "Blog → X Thread",
        "source_format": "blog",
        "target_format": "thread",
        "platform": "x",
        "max_pieces": 8,
    },
    "blog_to_linkedin": {
        "name": "Blog → LinkedIn Post",
        "source_format": "blog",
        "target_format": "post",
        "platform": "linkedin",
        "max_pieces": 1,
    },
    "blog_to_carousel": {
        "name": "Blog → Instagram Carousel",
        "source_format": "blog",
        "target_format": "carousel",
        "platform": "instagram",
        "max_pieces": 10,
    },
    "blog_to_reel": {
        "name": "Blog → Reel Script",
        "source_format": "blog",
        "target_format": "reel_script",
        "platform": "instagram",
        "max_pieces": 1,
    },
    "video_to_shorts": {
        "name": "Video → YouTube Shorts",
        "source_format": "video",
        "target_format": "short",
        "platform": "youtube",
        "max_pieces": 3,
    },
    "thread_to_post": {
        "name": "Thread → LinkedIn Post",
        "source_format": "thread",
        "target_format": "post",
        "platform": "linkedin",
        "max_pieces": 1,
    },
    "post_to_story": {
        "name": "Post → Story",
        "source_format": "post",
        "target_format": "story",
        "platform": "instagram",
        "max_pieces": 3,
    },
}

REPURPOSE_SYSTEM_PROMPTS = {
    "thread": (
        "Convert this content into an X/Twitter thread.\n"
        "Rules:\n"
        "- Start with a hook tweet\n"
        "- Each tweet ≤ 280 chars\n"
        "- Number tweets (1/, 2/, etc.)\n"
        "- End with a summary + CTA\n"
        "- 5-8 tweets optimal"
    ),
    "post": (
        "Convert this content into a LinkedIn post.\n"
        "Rules:\n"
        "- Start with a hook\n"
        "- Use line breaks\n"
        "- Keep under 3000 chars\n"
        "- End with question or CTA\n"
        "- 3-5 hashtags"
    ),
    "carousel": (
        "Convert this content into Instagram carousel slides.\n"
        "Rules:\n"
        "- Each slide is a key point\n"
        "- 5-10 slides\n"
        "- First slide = hook/title\n"
        "- Last slide = CTA\n"
        "- Short text per slide (under 30 words)"
    ),
    "reel_script": (
        "Convert this content into a Reel/Shorts video script.\n"
        "Rules:\n"
        "- Hook in first 3 seconds\n"
        "- 15-60 seconds total\n"
        "- Visual cues in [brackets]\n"
        "- End with CTA\n"
        "- Fast-paced, engaging"
    ),
    "short": (
        "Convert this content into YouTube Shorts scripts.\n"
        "Rules:\n"
        "- Under 60 seconds\n"
        "- Hook in first 2 seconds\n"
        "- One key takeaway per Short\n"
        "- Visual + text overlay cues\n"
        "- Subscribe CTA at end"
    ),
    "story": (
        "Convert this content into Instagram Story slides.\n"
        "Rules:\n"
        "- 3-5 story slides\n"
        "- Quick, visual content\n"
        "- Interactive elements (polls, questions)\n"
        "- Swipe-up CTA"
    ),
}


async def repurpose_content(
    content: str,
    source_format: str,
    target_formats: list[str],
    topic: str = "",
    tone: str = "professional",
    provider: str = "openai",
) -> dict[str, Any]:
    """Repurpose content into multiple target formats.

    Returns transformed content for each target format.
    """
    results: dict[str, Any] = {}

    for target in target_formats:
        route = REPURPOSE_ROUTES.get(target)
        if not route:
            results[target] = {"error": f"Unknown target format: {target}"}
            continue

        system_prompt = REPURPOSE_SYSTEM_PROMPTS.get(route["target_format"], "")
        if not system_prompt:
            results[target] = {"error": f"No prompt for format: {route['target_format']}"}
            continue

        user_prompt = f"Convert this content to {route['name']}:\n\n{content[:3000]}"
        if topic:
            user_prompt += f"\n\nTopic: {topic}"

        try:
            result = await call_llm_json(
                prompt=user_prompt,
                system_prompt=system_prompt,
                provider=provider,
                temperature=0.8,
            )

            if result:
                results[target] = {
                    "route": route["name"],
                    "platform": route["platform"],
                    "content": result if isinstance(result, str) else result.get("content", str(result)),
                    "pieces": result.get("pieces", []) if isinstance(result, dict) else [],
                }
            else:
                results[target] = {"error": "Generation failed"}

        except Exception as e:
            logger.error(f"Repurpose failed for {target}: {e}")
            results[target] = {"error": str(e)}

    return {
        "source_format": source_format,
        "repurposed_count": len([r for r in results.values() if "error" not in r]),
        "results": results,
    }


def get_available_routes(source_format: str | None = None) -> list[dict[str, Any]]:
    """Get available repurposing routes, optionally filtered by source format."""
    routes = []
    for key, route in REPURPOSE_ROUTES.items():
        if source_format and route["source_format"] != source_format:
            continue
        routes.append({
            "key": key,
            "name": route["name"],
            "source": route["source_format"],
            "target": route["target_format"],
            "platform": route["platform"],
        })
    return routes
