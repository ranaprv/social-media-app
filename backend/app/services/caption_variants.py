"""Caption Variant Generator — 3-5 caption variations per platform.

Generates multiple caption options for A/B testing and selection.
"""
import logging
from typing import Any

from app.services.llm import call_llm

logger = logging.getLogger(__name__)

VARIANT_SYSTEM_PROMPTS = {
    "linkedin": (
        "Generate 5 LinkedIn caption variants for the given topic.\n"
        "Each variant should have a different approach:\n"
        "1. Data-driven (numbers, stats)\n"
        "2. Story-based (personal anecdote)\n"
        "3. Question-based (engagement hook)\n"
        "4. List-based (actionable tips)\n"
        "5. Contrarian (hot take)\n\n"
        "Return as JSON array: [{\"variant\": 1, \"approach\": \"...\", \"caption\": \"...\", \"estimated_engagement\": \"high|medium|low\"}]"
    ),
    "x": (
        "Generate 5 tweet variants for the given topic.\n"
        "Each variant should use a different formula:\n"
        "1. One-liner punch\n"
        "2. Thread starter\n"
        "3. Question tweet\n"
        "4. Hot take\n"
        "5. Value bomb\n\n"
        "All must be under 280 characters.\n"
        "Return as JSON array."
    ),
    "instagram": (
        "Generate 5 Instagram caption variants.\n"
        "Each with a different hook style:\n"
        "1. Curiosity gap\n"
        "2. Number-first\n"
        "3. Relatable statement\n"
        "4. Confession/admission\n"
        "5. How-to teaser\n\n"
        "Include emojis and hashtags at the end.\n"
        "Return as JSON array."
    ),
    "facebook": (
        "Generate 5 Facebook post variants.\n"
        "Each with a different engagement approach:\n"
        "1. Question post\n"
        "2. Poll/this-or-that\n"
        "3. Story share\n"
        "4. Quick tip\n"
        "5. Community ask\n\n"
        "Keep under 250 characters for optimal reach.\n"
        "Return as JSON array."
    ),
    "youtube": (
        "Generate 5 YouTube description variants.\n"
        "Each optimized differently:\n"
        "1. SEO-focused (keywords)\n"
        "2. Engagement-focused (CTA)\n"
        "3. Value-focused (what viewers learn)\n"
        "4. Community-focused (subscribe ask)\n"
        "5. Curiosity-focused (teaser)\n\n"
        "Include timestamps placeholder.\n"
        "Return as JSON array."
    ),
}


async def generate_caption_variants(
    topic: str,
    platform: str,
    tone: str = "professional",
    count: int = 5,
    existing_content: str | None = None,
    provider: str = "openai",
) -> dict[str, Any]:
    """Generate multiple caption variants for A/B testing."""
    system_prompt = VARIANT_SYSTEM_PROMPTS.get(platform, VARIANT_SYSTEM_PROMPTS["linkedin"])

    user_prompt = f"Generate {count} caption variants for: {topic}\nTone: {tone}\n"
    if existing_content:
        user_prompt += f"Based on this content: {existing_content[:500]}\n"

    try:
        raw = await call_llm(
            prompt=user_prompt,
            system_prompt=system_prompt,
            provider=provider,
            temperature=0.8,
            max_tokens=2000,
        )

        if raw:
            import json
            # Try to parse JSON response
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]

            try:
                variants = json.loads(cleaned.strip())
                if isinstance(variants, list):
                    return {
                        "variants": variants,
                        "count": len(variants),
                        "platform": platform,
                        "topic": topic,
                    }
            except json.JSONDecodeError:
                pass

            # Fallback: parse manually
            variants = []
            lines = raw.strip().split("\n")
            current_variant = {}
            for line in lines:
                line = line.strip()
                if line.startswith(("1.", "2.", "3.", "4.", "5.", "-")):
                    if current_variant.get("caption"):
                        variants.append(current_variant)
                    current_variant = {"caption": line.lstrip("1234567890.- "), "approach": "variant"}
                elif line and current_variant and not current_variant.get("caption"):
                    current_variant["caption"] = line
                elif "approach" in line.lower() or "variant" in line.lower():
                    current_variant["approach"] = line
            if current_variant.get("caption"):
                variants.append(current_variant)

            return {
                "variants": variants[:count],
                "count": len(variants[:count]),
                "platform": platform,
                "topic": topic,
            }

    except Exception as e:
        logger.error(f"Caption variant generation failed: {e}")

    return {"variants": [], "count": 0, "error": "Generation failed"}
