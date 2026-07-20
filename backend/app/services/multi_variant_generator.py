"""Multi-variant content generator — generate N variants, score, rank.

Generates multiple content variants in parallel, scores each with the
quality rubric + viral predictor, and returns them ranked by combined score.
This lets users pick the best option or auto-select the winner.

Design:
    - Uses temperature variation for diversity (0.5, 0.7, 0.9)
    - Scores each variant with rubric (10 dimensions) + viral predictor
    - Combined score = 0.6 * rubric_score + 0.4 * viral_score
    - Returns all variants ranked, best first
"""
import asyncio
import logging
from typing import Any

from app.services.llm import call_llm
from app.services.content_quality_rubric import score_content_rubric
from app.services.viral_score import predict_viral_score

logger = logging.getLogger(__name__)

# Temperature presets for variant diversity
_TEMPERATURES = [0.5, 0.7, 0.9]

# Variant style instructions to force different angles
_VARIANT_ANGLES = [
    "",  # default — no angle instruction
    "Write from a contrarian or surprising angle. Challenge assumptions.",
    "Write a storytelling/narrative version. Use a personal anecdote or case study.",
]


async def generate_variants(
    system_prompt: str,
    user_prompt: str,
    platform: str,
    provider: str = "openai",
    model: str | None = None,
    variant_count: int = 3,
    media_count: int = 0,
    has_cta: bool = False,
    brand_voice: str | None = None,
    target_audience: str | None = None,
) -> dict[str, Any]:
    """Generate multiple content variants, score each, return ranked results.

    Args:
        system_prompt: The system prompt for generation
        user_prompt: The user prompt for generation
        platform: Target platform (linkedin, x, instagram, etc.)
        provider: LLM provider
        model: Optional model override
        variant_count: Number of variants to generate (1-5)
        media_count: Number of media files attached (for scoring)
        has_cta: Whether content has a CTA (for scoring)
        brand_voice: Brand voice description (for scoring)
        target_audience: Target audience (for scoring)

    Returns:
        {
            "variants": [...],          # all variants ranked
            "best_index": 0,            # index of best variant
            "best_content": "...",      # best variant's content
            "scores_summary": {...},    # aggregate scoring info
        }
    """
    variant_count = max(1, min(5, variant_count))

    # Generate variants in parallel with different temperatures
    tasks = []
    for i in range(variant_count):
        temp = _TEMPERATURES[i % len(_TEMPERATURES)]
        angle = _VARIANT_ANGLES[i % len(_VARIANT_ANGLES)]

        # Add angle instruction to user prompt
        variant_prompt = user_prompt
        if angle:
            variant_prompt = f"{user_prompt}\n\nSpecial instruction: {angle}"

        tasks.append(
            _generate_single_variant(
                system_prompt=system_prompt,
                user_prompt=variant_prompt,
                provider=provider,
                model=model,
                temperature=temp,
                variant_index=i,
            )
        )

    raw_results = await asyncio.gather(*tasks, return_exceptions=True)

    # Score each variant
    variants = []
    for i, result in enumerate(raw_results):
        if isinstance(result, Exception):
            logger.warning("Variant %d generation failed: %s", i, result)
            continue

        content = result.get("content", "")
        if not content:
            continue

        # Score with rubric
        rubric = score_content_rubric(
            content=content,
            platform=platform,
            media_count=media_count,
            has_cta=has_cta,
            brand_voice=brand_voice,
            target_audience=target_audience,
        )

        # Score with viral predictor
        viral = predict_viral_score(
            content=content,
            platform=platform,
            media_count=media_count,
        )

        # Combined score: 60% rubric + 40% viral
        combined = round(rubric["overall_score"] * 0.6 + viral["score"] * 0.4, 1)

        variants.append({
            "index": i,
            "content": content,
            "temperature": result.get("temperature", 0.7),
            "angle": _VARIANT_ANGLES[i % len(_VARIANT_ANGLES)] or "default",
            "rubric_score": rubric["overall_score"],
            "rubric_rating": rubric["rating"],
            "rubric_dimensions": rubric["dimensions"],
            "rubric_suggestions": rubric["suggestions"],
            "viral_score": viral["score"],
            "viral_factors": viral["factors"],
            "combined_score": combined,
        })

    if not variants:
        return {
            "variants": [],
            "best_index": -1,
            "best_content": "",
            "scores_summary": {"total_generated": 0, "total_scored": 0},
        }

    # Sort by combined score (best first)
    variants.sort(key=lambda v: v["combined_score"], reverse=True)

    # Re-index after sorting
    for i, v in enumerate(variants):
        v["rank"] = i + 1

    best = variants[0]

    return {
        "variants": variants,
        "best_index": 0,
        "best_content": best["content"],
        "scores_summary": {
            "total_generated": len(raw_results),
            "total_scored": len(variants),
            "avg_combined_score": round(
                sum(v["combined_score"] for v in variants) / len(variants), 1
            ),
            "best_combined_score": best["combined_score"],
            "score_range": {
                "min": variants[-1]["combined_score"],
                "max": best["combined_score"],
            },
        },
    }


async def _generate_single_variant(
    system_prompt: str,
    user_prompt: str,
    provider: str,
    model: str | None,
    temperature: float,
    variant_index: int,
) -> dict[str, Any]:
    """Generate a single content variant."""
    content = await call_llm(
        prompt=user_prompt,
        system_prompt=system_prompt,
        provider=provider,
        model=model,
        temperature=temperature,
        max_tokens=3000,
    )

    return {
        "content": content or "",
        "temperature": temperature,
        "variant_index": variant_index,
    }
