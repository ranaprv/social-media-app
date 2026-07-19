"""AI Ideas Generator — multi-LLM brainstorming with voting."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import json

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.llm import (
    call_llm_json, multi_model_brainstorm, vote_on_ideas,
    get_available_models, AVAILABLE_MODELS,
)

router = APIRouter(prefix="/ai/ideas", tags=["ai-ideas"])

IDEA_CATEGORIES = [
    "educational", "tutorials", "stories", "case-studies",
    "product-updates", "industry-news", "personal-branding",
    "tips", "mistakes", "comparisons", "myths",
]


@router.get("/models")
async def list_models():
    """List available LLM models by provider."""
    return {"models": get_available_models(), "all": AVAILABLE_MODELS}


@router.post("/generate")
async def generate_ideas(
    request: dict,
):
    """Generate content ideas using selected LLM model(s) with optional voting."""
    niche = request.get("niche", "")
    topic = request.get("topic", "")
    count = request.get("count", 10)
    providers = request.get("providers", [])  # ["openai", "anthropic", "gemini"]
    model = request.get("model", None)  # specific model ID
    provider = request.get("provider", "openai")  # single provider fallback
    use_voting = request.get("use_voting", False)
    custom_prompt = request.get("custom_prompt", "")

    if not niche and not topic:
        raise HTTPException(status_code=400, detail="Either 'niche' or 'topic' is required")

    # Build the brainstorming prompt — niche-focused, not industry-level
    context_parts = []
    if niche:
        context_parts.append(f"Niche: {niche}")
    if topic:
        context_parts.append(f"Topic to brainstorm around: {topic}")
    if custom_prompt:
        context_parts.append(f"Additional context: {custom_prompt}")

    context = "\n".join(context_parts) if context_parts else f"Niche topic: {niche or topic}"

    system_prompt = f"""You are a creative content strategist specializing in niche content.
Generate {count} unique, specific content ideas that are deeply rooted in the given niche/topic.
Each idea must be actionable and specific — not generic industry advice.

Return a JSON array. Each element must have:
- "title": catchy title (string)
- "description": 1-2 sentence description of the content piece (string)
- "category": one of {IDEA_CATEGORIES} (string)
- "content_type": "image" | "carousel" | "article" | "linkedin_post" | "short_video" | "long_video" | "reel" | "story" (string)
- "platforms": array of platform strings (linkedin, x, instagram, facebook, youtube)
- "estimated_engagement": "high" | "medium" | "low" (string)
- "tags": array of relevant niche tags (array of strings)
- "angles": array of 2-3 unique angles/hooks for this idea (array of strings)

Return ONLY valid JSON array, no markdown fences."""

    prompt = f"""{context}

Generate {count} content ideas that are specific to this niche, not generic.
Focus on unique angles, trending topics within this niche, and content that would
stand out from typical competitor content."""

    if use_voting and len(providers) > 1:
        # Multi-model brainstorming with voting
        multi_responses = await multi_model_brainstorm(
            prompt, system_prompt, providers=providers, temperature=0.8
        )
        ideas = vote_on_ideas(multi_responses)

        if not ideas:
            ideas = _fallback_ideas(niche or topic, count)

        for idea in ideas:
            if "id" not in idea:
                idea["id"] = str(uuid.uuid4())

        return {
            "ideas": ideas[:count],
            "method": "multi_model_voting",
            "providers_used": list(multi_responses.keys()),
            "providers_responded": [p for p, r in multi_responses.items() if r],
        }
    else:
        # Single model generation
        ideas = await call_llm_json(prompt, system_prompt, provider=provider, model=model)

        if not ideas or not isinstance(ideas, list):
            ideas = _fallback_ideas(niche or topic, count)

        for idea in ideas:
            if "id" not in idea:
                idea["id"] = str(uuid.uuid4())

        return {
            "ideas": ideas[:count],
            "method": "single_model",
            "provider": provider,
            "model": model,
        }


def _fallback_ideas(niche: str, count: int) -> list[dict]:
    """Placeholder ideas when AI is unavailable."""
    templates = [
        ("Deep Dive: {niche} Fundamentals Explained", "educational", "article", "high"),
        ("Top 5 {niche} Mistakes Beginners Make", "mistakes", "carousel", "high"),
        ("{niche} vs Traditional Approach: Which Wins?", "comparisons", "linkedin_post", "medium"),
        ("Behind the Scenes: Our {niche} Process", "stories", "short_video", "medium"),
        ("Quick Tip: {niche} Hack You Need to Know", "tips", "reel", "high"),
        ("Case Study: How {niche} Changed Everything", "case-studies", "article", "high"),
        ("Tutorial: Master {niche} in 10 Minutes", "tutorials", "long_video", "medium"),
        ("Myth Busted: Common {niche} Misconceptions", "myths", "carousel", "medium"),
        ("Personal Brand: Building Authority in {niche}", "personal-branding", "linkedin_post", "medium"),
        ("Industry Update: What's New in {niche}", "industry-news", "image", "low"),
    ]
    ideas = []
    for i in range(min(count, len(templates))):
        title_tpl, category, content_type, engagement = templates[i]
        ideas.append({
            "id": str(uuid.uuid4()),
            "title": title_tpl.format(niche=niche),
            "description": f"Create engaging {category} content about {niche}.",
            "category": category,
            "content_type": content_type,
            "platforms": ["linkedin", "x"],
            "estimated_engagement": engagement,
            "tags": [niche, category],
            "angles": [f"Approach from a {category} perspective", f"Focus on practical takeaways"],
            "vote_count": 0,
            "voted_by": [],
        })
    return ideas
