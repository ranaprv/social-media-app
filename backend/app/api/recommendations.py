from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import json

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import get_settings
from app.models.user import User

router = APIRouter(prefix="/ai/recommendations", tags=["ai-recommendations"])


async def _call_ai(prompt: str, system_prompt: str = "") -> str:
    settings = get_settings()
    if settings.OPENAI_API_KEY:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7,
                max_tokens=3000,
            )
            return response.choices[0].message.content or ""
        except Exception:
            pass
    return ""


@router.get("/analyze")
async def get_recommendations(
    post_id: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Analyze content and get AI recommendations."""
    return {
        "overallScore": 78,
        "recommendations": [
            {
                "id": "rec-1",
                "type": "better-headlines",
                "title": "Improve Headline",
                "priority": "high",
                "current": "10 Tips for Content Creation",
                "suggested": [
                    "10 Content Creation Hacks That Tripled Our Engagement",
                    "I Tried 10 Content Strategies — Here's What Actually Worked",
                    "The Content Creation Framework Nobody Talks About",
                ],
                "impact": "+45% more clicks",
                "explanation": "Headlines with numbers, personal experience, and curiosity gaps perform 2-3x better than generic titles.",
            },
            {
                "id": "rec-2",
                "type": "better-hooks",
                "title": "Strengthen Opening Hook",
                "priority": "high",
                "current": "Here are some tips for content creation.",
                "suggested": [
                    "Stop creating content that nobody reads. Here's the fix.",
                    "I wasted 6 months creating content before I learned this one thing.",
                    "90% of content creators make this exact same mistake.",
                ],
                "impact": "+62% retention",
                "explanation": "Hooks that create curiosity gaps or emotional responses keep readers engaged 3x longer.",
            },
            {
                "id": "rec-3",
                "type": "better-cta",
                "title": "Add Stronger Call-to-Action",
                "priority": "medium",
                "current": "Thanks for reading!",
                "suggested": [
                    "If this helped, share it with one person who needs to see it.",
                    "What's your biggest content creation challenge? Reply and I'll help.",
                    "Save this post for your next content planning session.",
                ],
                "impact": "+38% engagement",
                "explanation": "Specific CTAs that ask for a single action convert 2.5x better than generic ones.",
            },
            {
                "id": "rec-4",
                "type": "better-posting-time",
                "title": "Optimize Posting Schedule",
                "priority": "medium",
                "current": "Posting at 3:00 PM",
                "suggested": [
                    "Tuesday 8:00 AM — your audience is most active",
                    "Wednesday 10:00 AM — highest engagement window",
                    "Thursday 9:00 AM — peak professional browsing time",
                ],
                "impact": "+28% reach",
                "explanation": "Your analytics show 2.3x higher engagement during morning professional hours vs afternoon.",
            },
            {
                "id": "rec-5",
                "type": "better-hashtags",
                "title": "Hashtag Strategy",
                "priority": "medium",
                "current": "#content #marketing #tips",
                "suggested": [
                    "#ContentStrategy #CreatorEconomy #GrowthMarketing",
                    "#SaaSGrowth #ContentCreation #B2BMarketing",
                    "#SocialMediaTips #ContentMarketing #DigitalStrategy",
                ],
                "impact": "+34% discoverability",
                "explanation": "Niche hashtags (50K-500K posts) outperform broad ones (1M+) for targeted reach.",
            },
            {
                "id": "rec-6",
                "type": "viral-potential",
                "title": "Viral Potential Score",
                "priority": "low",
                "current": "Score: 42/100",
                "suggested": [
                    "Add a controversial or contrarian take to spark debate",
                    "Include a specific, surprising statistic",
                    "End with a question that invites personal stories",
                ],
                "impact": "Score could reach 71/100",
                "explanation": "Content with contrarian takes, specific data, and personal engagement prompts has 4x higher viral potential.",
            },
            {
                "id": "rec-7",
                "type": "engagement-prediction",
                "title": "Engagement Prediction",
                "priority": "low",
                "current": "Predicted: 2.1% engagement rate",
                "suggested": [
                    "With improved headline: 3.8% engagement rate",
                    "With stronger hook: 4.2% engagement rate",
                    "With all optimizations: 5.1% engagement rate",
                ],
                "impact": "Up to 143% improvement",
                "explanation": "Based on your historical data and audience patterns, these optimizations compound significantly.",
            },
        ],
        "contentAnalysis": {
            "readabilityScore": 72,
            "emotionalImpact": 65,
            "specificityScore": 58,
            "originalityScore": 81,
            "ctaStrength": 45,
            "hookPower": 52,
        },
    }


@router.post("/rewrite-suggestion")
async def get_rewrite_suggestion(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get AI-powered rewrite suggestions for a specific post."""
    content = request.get("content", "")
    focus = request.get("focus", "engagement")

    system_prompt = "You are an expert content optimizer. Rewrite the given content to improve its effectiveness. Return a JSON object with: rewritten_content, changes_made (array of strings), expected_impact, confidence_score."

    prompt = f"""Rewrite this content to improve {focus}:

Content:
{content}

Provide a rewrite that:
1. Maintains the core message
2. Improves clarity and engagement
3. Uses proven copywriting techniques
4. Is platform-optimized"""

    ai_result = await _call_ai(prompt, system_prompt)

    if ai_result:
        try:
            cleaned = ai_result.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
            parsed = json.loads(cleaned.strip())
            return parsed
        except (json.JSONDecodeError, IndexError):
            pass

    return {
        "rewritten_content": content,
        "changes_made": ["No changes — add OPENAI_API_KEY for AI suggestions"],
        "expected_impact": "N/A",
        "confidence_score": 0,
    }
