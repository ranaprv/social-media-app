from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import json

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import get_settings
from app.models.user import User

router = APIRouter(prefix="/ai/repurpose", tags=["ai-repurpose"])

OUTPUT_PLATFORM_MAP = {
    "linkedin-post": "linkedin",
    "twitter-thread": "x",
    "facebook-post": "facebook",
    "instagram-caption": "instagram",
    "carousel-copy": "linkedin",
    "newsletter": "linkedin",
    "youtube-shorts-script": "youtube",
    "reel-script": "instagram",
    "email": "linkedin",
}

OUTPUT_TYPE_LABELS = {
    "linkedin-post": "LinkedIn Post",
    "twitter-thread": "X/Twitter Thread",
    "facebook-post": "Facebook Post",
    "instagram-caption": "Instagram Caption",
    "carousel-copy": "Carousel Copy",
    "newsletter": "Newsletter",
    "youtube-shorts-script": "YouTube Shorts Script",
    "reel-script": "Reel Script",
    "email": "Email",
}


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


def _extract_text_from_url(url: str) -> str:
    """Placeholder for URL content extraction."""
    return f"[Content extracted from {url}]\n\nThis would contain the full text content from the URL. Connect a content extraction service (Jina, Firecrawl, or similar) for real extraction."


def _generate_placeholder(content: str, output_type: str, tone: str) -> str:
    topic = content[:200] if content else "this topic"
    templates = {
        "linkedin-post": f"🚀 {topic}\n\nHere's what most people miss:\n\n1. Start with value, not promotion\n2. Share real experiences, not theory\n3. Engage with your community\n\nThe key insight? Consistency beats perfection every time.\n\nWhat's your take? Drop a comment below 👇\n\n#ContentMarketing #GrowthHacking",
        "twitter-thread": f"🧵 Thread: {topic}\n\nMost people get this wrong. Here's what actually works 👇\n\n1/5 The first thing to understand is that this isn't about luck — it's about system design.\n\n2/5 When you focus on the fundamentals, everything else falls into place.\n\n3/5 The biggest mistake? Trying to do everything at once.\n\n4/5 Start small, measure, iterate. That's the playbook.\n\n5/5 If this was helpful, RT the first tweet and follow for more insights.",
        "facebook-post": f"Hey everyone! 👋\n\nLet's talk about {topic}.\n\nI've been thinking about this a lot lately, and here's my honest take:\n\nThe biggest mistake people make is overcomplicating it. Keep it simple, focus on providing value, and the results will follow.\n\nWhat do you think? Agree or disagree? Let me know in the comments! 💬",
        "instagram-caption": f"✨ {topic} ✨\n\nSave this for later! 📌\n\nHere's the truth nobody tells you:\n\n💡 It starts with understanding your audience\n📊 Data beats guesswork every time\n🎯 Consistency is the real hack\n\nDouble tap if you agree! ❤️\n\n#ContentCreator #SocialMediaTips #GrowthMindset",
        "carousel-copy": f"Slide 1: {topic} — A Complete Guide\n\nSlide 2: Why This Matters\nMost people overlook this. Here's why it's critical for your growth.\n\nSlide 3: The Problem\n80% of creators struggle with this. Sound familiar?\n\nSlide 4: The Solution\nStep-by-step breakdown of what actually works.\n\nSlide 5: Key Takeaways\n• Start with value\n• Be consistent\n• Measure everything\n\nSlide 6: Your Next Step\nSave this post and try it today. Tag someone who needs this!",
        "newsletter": f"Subject: The {topic} Playbook\n\nHi [Name],\n\nThis week, I want to share something that changed how I think about {topic}.\n\nThe core insight is simple but powerful:\n\n[Main insight would go here]\n\nHere's the 3-step framework:\n\nStep 1: [Foundation]\nStep 2: [Execution]\nStep 3: [Optimization]\n\nTry this out this week and let me know how it goes.\n\nBest,\n[Your Name]\n\nP.S. Reply to this email with your biggest challenge — I read every response.",
        "youtube-shorts-script": f"[HOOK - 0:00-0:03]\nStop scrolling! Here's what you need to know about {topic}.\n\n[CONTENT - 0:03-0:25]\nMost people make this mistake. The fix is actually simple.\n\nHere's the 3-step process:\n1. First, understand the fundamentals\n2. Then, apply consistently\n3. Finally, measure and iterate\n\n[CTA - 0:25-0:30]\nFollow for more tips! Drop a 🔥 if this helped!",
        "reel-script": f'[Opening Scene - Trending Audio]\nText overlay: "POV: You finally understand {topic}"\n\n[Scene 1]\nShow the "before" — struggling, confused, overwhelmed\nText: "When I first started..."\n\n[Scene 2]\nTransition to "after" — confident, successful\nText: "But then I discovered this..."\n\n[Scene 3]\nQuick tips flying in\nText: "Step 1... Step 2... Step 3..."\n\n[End Scene]\nText: "Save this for later! 📌"\n\nCaption: The {topic} transformation nobody talks about ✨',
        "email": f"Subject: Quick thought on {topic}\n\nHi [Name],\n\nI wanted to share something quick about {topic} that's been on my mind.\n\n[Key insight]\n\nHere's why this matters for you:\n• [Benefit 1]\n• [Benefit 2]\n• [Benefit 3]\n\nIf you want to go deeper, [CTA].\n\nBest,\n[Your Name]",
    }
    return templates.get(output_type, f"[{output_type}] Content about: {topic}")


@router.post("/generate")
async def repurpose_content(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Repurpose content into multiple platform-specific formats."""
    input_type = request.get("input_type", "markdown")
    input_content = request.get("input_content", "")
    input_url = request.get("input_url")
    output_types = request.get("output_types", [])
    tone = request.get("tone", "professional")
    # New mode-based repurposing
    mode = request.get("mode")
    input_text = request.get("input", "")
    platform = request.get("platform", "linkedin")

    if mode:
        # Mode-based repurposing (new frontend)
        outputs = request.get("outputs", [])
        content = input_text or input_content or ""
        if not content:
            raise HTTPException(status_code=400, detail="Input content is required")

        results = []
        for output_name in outputs:
            ai_result = await _call_ai(
                f"Repurpose this into a {output_name} with {tone} tone for {platform}:\n\n{content[:2000]}",
                f"You are an expert content repurposer. Create platform-optimized content for {output_name}."
            )
            final_content = ai_result if ai_result else _generate_placeholder(content[:300], output_name.lower().replace(" ", "-"), tone)
            results.append({"title": output_name, "content": final_content, "platform": platform})

        return {"results": results}


    if not input_content and not input_url:
        raise HTTPException(status_code=400, detail="Input content or URL is required")
    if not output_types:
        raise HTTPException(status_code=400, detail="At least one output type is required")

    # Extract content from URL if provided
    if input_url and not input_content:
        input_content = _extract_text_from_url(input_url)

    system_prompt = """You are an expert content repurposer. Transform the given content into platform-specific formats.
Each output should be optimized for its target platform's best practices, character limits, and audience behavior.
Return a JSON array of objects with: output_type, content, hashtags (array), estimated_engagement (high/medium/low).
Return ONLY valid JSON, no markdown."""

    results = []
    for output_type in output_types:
        platform = OUTPUT_PLATFORM_MAP.get(output_type, "linkedin")
        label = OUTPUT_TYPE_LABELS.get(output_type, output_type)

        prompt = f"""Repurpose this content into a {label}:

Original content:
{input_content[:2000]}

Tone: {tone}
Target platform: {platform}
Output type: {output_type}

Make it platform-optimized with appropriate hashtags and engagement tactics."""

        ai_result = await _call_ai(prompt, system_prompt)

        content = ""
        if ai_result:
            try:
                cleaned = ai_result.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("\n", 1)[1]
                if cleaned.endswith("```"):
                    cleaned = cleaned.rsplit("```", 1)[0]
                parsed = json.loads(cleaned.strip())
                if isinstance(parsed, list) and len(parsed) > 0:
                    item = parsed[0]
                    content = item.get("content", "")
            except (json.JSONDecodeError, IndexError):
                pass

        if not content:
            content = _generate_placeholder(input_content[:300], output_type, tone)

        results.append({
            "id": str(uuid.uuid4()),
            "output_type": output_type,
            "content": content,
            "hashtags": [f"#{word.capitalize()}" for word in (input_content[:50]).split()[:5]],
            "platform": platform,
            "estimated_engagement": "medium",
        })

    return {
        "results": results,
        "summary": f"Repurposed content into {len(results)} platform-specific formats.",
    }
