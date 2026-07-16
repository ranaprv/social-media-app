from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import json

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import get_settings
from app.models.user import User
from app.models.workspace import WorkspaceMember
from app.schemas import AIResearchIdeasResponse

router = APIRouter(prefix="/ai/ideas", tags=["ai-ideas"])

IDEA_CATEGORIES = [
    "educational", "tutorials", "stories", "case-studies",
    "product-updates", "industry-news", "personal-branding",
    "tips", "mistakes", "comparisons", "myths",
]

PLATFORMS = ["linkedin", "x", "instagram", "facebook", "youtube"]


async def _call_ai(prompt: str, system_prompt: str = "") -> str:
    """Call OpenAI or return placeholder."""
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
                temperature=0.8,
                max_tokens=3000,
            )
            return response.choices[0].message.content or ""
        except Exception:
            pass
    return ""


def _placeholder_ideas(industry: str, keywords: list[str], count: int) -> list[dict]:
    """Generate placeholder ideas when AI is unavailable."""
    templates = [
        ("How {industry} is Changing in 2026", "educational", "high"),
        ("Top {n} Mistakes in {industry}", "mistakes", "high"),
        ("{keyword} vs {keyword}: Which is Better?", "comparisons", "medium"),
        ("Myths About {keyword} Debunked", "myths", "medium"),
        ("Case Study: How We Used {keyword}", "case-studies", "high"),
        ("Tutorial: Getting Started with {keyword}", "tutorials", "high"),
        ("Behind the Scenes: Our {industry} Journey", "stories", "medium"),
        ("Quick Tips for {keyword}", "tips", "medium"),
        ("What's New in {industry} This Month", "industry-news", "low"),
        ("How to Build Your Personal Brand in {industry}", "personal-branding", "medium"),
        ("Product Update: New {keyword} Features", "product-updates", "low"),
        ("The Future of {keyword} in {industry}", "educational", "high"),
    ]
    ideas = []
    for i in range(min(count, len(templates))):
        title_tpl, category, engagement = templates[i]
        kw = keywords[i % len(keywords)] if keywords else industry
        title = title_tpl.format(
            industry=industry, keyword=kw, keyword2=keywords[(i + 1) % len(keywords)] if len(keywords) > 1 else kw,
            n=len(keywords) or 5,
        )
        ideas.append({
            "id": str(uuid.uuid4()),
            "title": title,
            "description": f"Create engaging {category} content about {kw} for {industry} audience.",
            "category": category,
            "platforms": ["linkedin", "x"],
            "estimated_engagement": engagement,
            "tags": [kw, industry, category],
        })
    return ideas


@router.post("/generate")
async def generate_ideas(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate content ideas based on industry context."""
    industry = request.get("industry", "")
    keywords = request.get("keywords", [])
    audience = request.get("audience", "")
    competitors = request.get("competitors", [])
    products = request.get("products", [])
    website_url = request.get("website_url")
    count = request.get("count", 10)
    categories = request.get("categories", [])

    if not industry:
        raise HTTPException(status_code=400, detail="Industry is required")

    # Build prompt
    system_prompt = """You are a content strategy expert. Generate content ideas as a JSON array.
Each idea must have: id (uuid), title, description, category, platforms (array), estimated_engagement (high/medium/low), tags (array).
Categories: educational, tutorials, stories, case-studies, product-updates, industry-news, personal-branding, tips, mistakes, comparisons, myths.
Platforms: linkedin, x, instagram, facebook, youtube.
Return ONLY valid JSON array, no markdown."""

    prompt_parts = [f"Generate {count} content ideas for the {industry} industry."]
    if keywords:
        prompt_parts.append(f"Keywords: {', '.join(keywords)}")
    if audience:
        prompt_parts.append(f"Target audience: {audience}")
    if competitors:
        prompt_parts.append(f"Competitors to reference: {', '.join(competitors)}")
    if products:
        prompt_parts.append(f"Products/services: {', '.join(products)}")
    if website_url:
        prompt_parts.append(f"Website: {website_url}")
    if categories:
        prompt_parts.append(f"Focus on categories: {', '.join(categories)}")
    else:
        prompt_parts.append(f"Spread across all categories: {', '.join(IDEA_CATEGORIES)}")

    full_prompt = "\n".join(prompt_parts)

    ai_response = await _call_ai(full_prompt, system_prompt)

    ideas = []
    if ai_response:
        try:
            # Strip markdown code fences if present
            cleaned = ai_response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
            cleaned = cleaned.strip()
            parsed = json.loads(cleaned)
            if isinstance(parsed, list):
                ideas = parsed
        except (json.JSONDecodeError, IndexError):
            pass

    if not ideas:
        ideas = _placeholder_ideas(industry, keywords, count)

    # Ensure IDs and limit count
    for idea in ideas:
        if "id" not in idea:
            idea["id"] = str(uuid.uuid4())
    ideas = ideas[:count]

    return {"ideas": ideas}
