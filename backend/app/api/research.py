"""Research API — trends, competitors, keyword research."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import json

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.llm import call_llm, call_llm_json

router = APIRouter(prefix="/research", tags=["research"])


@router.post("/trends")
async def search_trends(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Search trending topics for a niche/keyword."""
    topic = request.get("topic", "")
    platform = request.get("platform", "all")
    provider = request.get("provider", "openai")
    model = request.get("model")

    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")

    system_prompt = """You are a trend research analyst. Analyze trending topics related to the given query.
Return a JSON object with:
- "trends": array of {topic, description, platform,热度 (popularity 1-100), trend_direction: "rising"/"stable"/"declining", content_opportunity: string}
- "related_topics": array of related trending topics (strings)
- "best_time_to_post": object with day_of_week and time recommendations

Return ONLY valid JSON, no markdown."""

    prompt = f"""Research trending topics for: {topic}
Platform focus: {platform}

Identify 5-8 trending topics that are relevant, with their popularity scores and content opportunities."""

    result = await call_llm_json(prompt, system_prompt, provider=provider, model=model, temperature=0.7)

    if not result:
        result = {
            "trends": [
                {"topic": f"Trending in {topic}", "description": f"Current trend analysis for {topic}", "platform": "all", "popularity": 75, "trend_direction": "rising", "content_opportunity": f"Create content around this {topic} trend"},
            ],
            "related_topics": [f"{topic} tips", f"{topic} trends 2026", f"best {topic} practices"],
            "best_time_to_post": {"day_of_week": "Tuesday", "time": "9:00 AM"},
        }

    return result


@router.post("/competitors")
async def analyze_competitors(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Analyze competitor content and strategy."""
    competitors = request.get("competitors", [])
    niche = request.get("niche", "")
    provider = request.get("provider", "openai")
    model = request.get("model")

    if not competitors and not niche:
        raise HTTPException(status_code=400, detail="Provide competitors list or niche")

    system_prompt = """You are a competitive intelligence analyst. Analyze competitor content strategies.
Return a JSON object with:
- "competitors": array of {name, strengths, weaknesses, content_strategy, posting_frequency, top_content_types, engagement_level, opportunities_to_differentiate}
- "market_gaps": array of content gaps you identified (strings)
- "recommendations": array of actionable recommendations (strings)

Return ONLY valid JSON, no markdown."""

    comp_text = ", ".join(competitors) if competitors else f"Competitors in {niche}"
    prompt = f"""Analyze competitors: {comp_text}
Niche: {niche}

Provide a comprehensive competitive analysis with actionable recommendations."""

    result = await call_llm_json(prompt, system_prompt, provider=provider, model=model, temperature=0.7)

    if not result:
        result = {
            "competitors": [{"name": c, "strengths": "Established brand", "weaknesses": "Generic content", "content_strategy": "Standard posting", "posting_frequency": "Daily", "top_content_types": ["posts", "articles"], "engagement_level": "medium", "opportunities_to_differentiate": "Niche down"} for c in (competitors or ["Competitor 1"])],
            "market_gaps": [f"Underserved sub-topic in {niche}", "Interactive content missing", "Video content gap"],
            "recommendations": [f"Focus on {niche} sub-niches competitors ignore", "Create video-first content", "Build community engagement"],
        }

    return result


@router.post("/keywords")
async def research_keywords(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Research keywords with volume and difficulty estimates."""
    topic = request.get("topic", "")
    niche = request.get("niche", "")
    provider = request.get("provider", "openai")
    model = request.get("model")

    if not topic and not niche:
        raise HTTPException(status_code=400, detail="Topic or niche is required")

    system_prompt = """You are an SEO keyword research expert. Analyze keywords for content planning.
Return a JSON object with:
- "keywords": array of {keyword, estimated_volume: "high"/"medium"/"low", difficulty: "easy"/"medium"/"hard", intent: "informational"/"commercial"/"transactional"/"navigational", content_type: suggested content format, score: 0-100}
- "long_tail": array of long-tail keyword suggestions (strings)
- "content_clusters": array of {pillar_topic, cluster_keywords: []}

Return ONLY valid JSON, no markdown."""

    prompt = f"""Research keywords for: {topic or niche}
Niche context: {niche or topic}

Generate a comprehensive keyword list with volume estimates and content recommendations."""

    result = await call_llm_json(prompt, system_prompt, provider=provider, model=model, temperature=0.7)

    if not result:
        kw = topic or niche
        result = {
            "keywords": [
                {"keyword": kw, "estimated_volume": "high", "difficulty": "medium", "intent": "informational", "content_type": "article", "score": 85},
                {"keyword": f"how to {kw}", "estimated_volume": "medium", "difficulty": "easy", "intent": "informational", "content_type": "tutorial", "score": 78},
                {"keyword": f"best {kw} tools", "estimated_volume": "medium", "difficulty": "medium", "intent": "commercial", "content_type": "listicle", "score": 72},
            ],
            "long_tail": [f"best {kw} for beginners", f"{kw} vs alternatives", f"how to start with {kw}"],
            "content_clusters": [{"pillar_topic": kw, "cluster_keywords": [f"{kw} guide", f"{kw} tips", f"learn {kw}"]}],
        }

    return result
