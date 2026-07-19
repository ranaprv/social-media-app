"""Content gap analyzer — identify what topics are missing.

Analyzes existing content against topic coverage to find gaps
in the content strategy.
"""
import logging
from typing import Any

from app.services.llm import call_llm_json

logger = logging.getLogger(__name__)


async def analyze_content_gaps(
    existing_topics: list[str],
    industry: str,
    target_audience: str = "professionals",
    platforms: list[str] | None = None,
    competitor_topics: list[str] | None = None,
    provider: str = "openai",
) -> dict[str, Any]:
    """Analyze content gaps and suggest missing topics.

    Compares existing content topics against industry standards
    and competitor coverage to identify opportunities.
    """
    system_prompt = (
        "You are a content strategy analyst. "
        "Analyze the content gaps and return JSON.\n\n"
        "Return a JSON object with:\n"
        '- "gaps": [{topic, reason, priority, suggested_content_type, platforms}]\n'
        '- "coverage_score": 0-100\n'
        '- "top_opportunities": [{topic, rationale}]\n'
        '- "competitor_gaps": [{topic, why_it_matters}]\n'
    )

    user_prompt = (
        f"Analyze content gaps for {industry} industry.\n\n"
        f"Existing topics covered: {', '.join(existing_topics[:20])}\n"
        f"Audience: {target_audience}\n"
        f"Platforms: {', '.join(platforms or ['linkedin', 'x'])}\n"
    )

    if competitor_topics:
        user_prompt += f"Competitor topics: {', '.join(competitor_topics[:20])}\n"

    user_prompt += (
        "\nIdentify:\n"
        "- Missing topics that competitors cover\n"
        "- Underserved audience needs\n"
        "- Trending topics not yet covered\n"
        "- Content format gaps (e.g., no video content)\n"
    )

    try:
        result = await call_llm_json(
            prompt=user_prompt,
            system_prompt=system_prompt,
            provider=provider,
            temperature=0.8,
        )

        if result and isinstance(result, dict):
            return {
                "gaps": result.get("gaps", []),
                "coverage_score": result.get("coverage_score", 50),
                "top_opportunities": result.get("top_opportunities", []),
                "competitor_gaps": result.get("competitor_gaps", []),
                "existing_topics_count": len(existing_topics),
                "industry": industry,
            }

    except Exception as e:
        logger.error(f"Gap analysis failed: {e}")

    return {
        "gaps": [],
        "coverage_score": 0,
        "top_opportunities": [],
        "competitor_gaps": [],
        "error": "Analysis failed",
    }
