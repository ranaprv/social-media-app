"""Audience Persona Builder — define target segments for content strategy.

Creates detailed audience personas with content preferences and engagement patterns.
"""
import logging
from typing import Any

from app.services.llm import call_llm_json

logger = logging.getLogger(__name__)

# Default persona templates
PERSONA_TEMPLATES = [
    {
        "id": "decision-maker",
        "name": "Decision Maker",
        "description": "C-suite and senior leaders who make purchasing decisions",
        "demographics": {"role": "C-Suite / VP", "company_size": "50-500", "experience": "10+ years"},
        "content_preferences": ["thought leadership", "ROI data", "case studies", "industry trends"],
        "best_platforms": ["linkedin"],
        "optimal_posting_times": ["weekday mornings"],
        "engagement_style": "quality over quantity",
    },
    {
        "id": "practitioner",
        "name": "Practitioner",
        "description": "Hands-on professionals who use tools daily",
        "demographics": {"role": "Manager / IC", "company_size": "10-200", "experience": "3-8 years"},
        "content_preferences": ["how-to guides", "tutorials", "tips", "tool comparisons"],
        "best_platforms": ["linkedin", "x"],
        "optimal_posting_times": ["weekday mornings and lunch"],
        "engagement_style": "practical and actionable",
    },
    {
        "id": "creator",
        "name": "Content Creator",
        "description": "Individual creators building personal brands",
        "demographics": {"role": "Freelancer / Creator", "company_size": "1-10", "experience": "2-5 years"},
        "content_preferences": ["behind-the-scenes", "growth stories", "tools", "monetization"],
        "best_platforms": ["instagram", "x", "youtube"],
        "optimal_posting_times": ["evenings and weekends"],
        "engagement_style": "community-driven",
    },
]


async def build_audience_persona(
    industry: str,
    product_type: str,
    existing_audience_data: dict[str, Any] | None = None,
    provider: str = "openai",
) -> dict[str, Any]:
    """Build a detailed audience persona using AI.

    Combines industry knowledge with any existing audience data.
    """
    system_prompt = (
        "You are an audience research expert. "
        "Build a detailed audience persona as JSON.\n\n"
        "Return:\n"
        '- "persona_name": descriptive name\n'
        '- "demographics": {role, company_size, industry, experience, location}\n'
        '- "psychographics": {values, interests, pain_points, goals, objections}\n'
        '- "content_preferences": [types of content they engage with]\n'
        '- "platform_behavior": {platform: behavior description}\n'
        '- "buying_journey": {awareness, consideration, decision, retention}\n'
        '- "engagement_patterns": {best_times, content_types, topics}\n'
        '- "messaging_angle": what resonates with this persona\n'
    )

    user_prompt = (
        f"Build an audience persona for:\n"
        f"Industry: {industry}\n"
        f"Product/Service: {product_type}\n"
    )

    if existing_audience_data:
        user_prompt += f"Existing audience data: {existing_audience_data}\n"

    try:
        result = await call_llm_json(
            prompt=user_prompt,
            system_prompt=system_prompt,
            provider=provider,
            temperature=0.7,
        )

        if result and isinstance(result, dict):
            return {
                "persona": result,
                "templates": PERSONA_TEMPLATES,
            }

    except Exception as e:
        logger.error(f"Persona building failed: {e}")

    return {"persona": None, "templates": PERSONA_TEMPLATES, "error": "Building failed"}


def get_persona_templates() -> list[dict[str, Any]]:
    """Get default persona templates."""
    return PERSONA_TEMPLATES
