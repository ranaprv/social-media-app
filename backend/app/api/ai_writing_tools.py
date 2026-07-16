from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import get_settings
from app.models.user import User
from app.models.workspace import WorkspaceMember

router = APIRouter(prefix="/ai/writing-tools", tags=["ai-writing-tools"])

TOOL_PROMPTS = {
    "rewrite": {
        "system": "You are an expert content rewriter. Rewrite the given content to improve clarity, engagement, and impact while preserving the core message. Adapt to the specified platform if provided.",
        "prompt": "Rewrite this content:\n\n{content}",
    },
    "expand": {
        "system": "You are a content expansion expert. Take the given content and expand it with more detail, examples, and depth while maintaining the original tone and message.",
        "prompt": "Expand this content with more detail and examples:\n\n{content}",
    },
    "summarize": {
        "system": "You are an expert summarizer. Create a concise, clear summary of the given content that captures all key points.",
        "prompt": "Summarize this content concisely:\n\n{content}",
    },
    "translate": {
        "system": "You are a professional translator. Translate the content to the target language while maintaining tone, idioms, and cultural context.",
        "prompt": "Translate this content to {target_language}:\n\n{content}",
    },
    "improve-grammar": {
        "system": "You are a professional editor. Fix all grammar, spelling, punctuation, and style issues. Improve readability while preserving the author's voice.",
        "prompt": "Fix grammar and improve this content:\n\n{content}",
    },
    "generate-hooks": {
        "system": "You are a hook-writing expert. Generate 5 compelling hooks (opening lines) for social media content that grab attention and drive engagement. Each hook should use a different technique (question, statistic, story, contrarian, curiosity gap).",
        "prompt": "Generate 5 hooks for content about:\n\n{content}",
    },
    "generate-ctas": {
        "system": "You are a CTA (call-to-action) specialist. Generate 5 effective CTAs that drive specific actions. Each CTA should use a different approach (question, urgency, value proposition, social proof, direct ask).",
        "prompt": "Generate 5 CTAs for content about:\n\n{content}",
    },
    "generate-hashtags": {
        "system": "You are a hashtag strategist. Generate relevant, trending hashtags organized by tier: 3 high-volume broad tags, 5 mid-volume niche tags, and 5 low-volume specific tags. Total 13 hashtags.",
        "prompt": "Generate a hashtag strategy for content about:\n\n{content}",
    },
    "seo-optimize": {
        "system": "You are an SEO content optimizer. Optimize the given content for search engines by improving keyword placement, headings, meta description suggestions, and readability. Maintain natural flow.",
        "prompt": "SEO-optimize this content:\n\n{content}",
    },
    "tone-adjust": {
        "system": "You are a tone adjustment expert. Rewrite the content to match the specified tone while keeping the core message intact.",
        "prompt": "Adjust the tone of this content to be {target_tone}:\n\n{content}",
    },
}


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
                temperature=0.7,
                max_tokens=2000,
            )
            return response.choices[0].message.content or ""
        except Exception:
            pass
    return ""


@router.post("")
async def use_writing_tool(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Use an AI writing tool on content."""
    tool = request.get("tool", "")
    content = request.get("content", "")
    platform = request.get("platform")
    target_language = request.get("target_language")
    target_tone = request.get("target_tone")
    keywords = request.get("keywords", [])

    if not tool:
        raise HTTPException(status_code=400, detail="Tool is required")
    if not content:
        raise HTTPException(status_code=400, detail="Content is required")
    if tool not in TOOL_PROMPTS:
        raise HTTPException(status_code=400, detail=f"Unknown tool: {tool}")

    tool_config = TOOL_PROMPTS[tool]
    system_prompt = tool_config["system"]

    # Build platform context
    platform_context = ""
    if platform:
        platform_context = f"\nPlatform: {platform}. Adapt the output for {platform} best practices."
    if keywords:
        platform_context += f"\nKeywords to incorporate: {', '.join(keywords)}"

    # Format prompt with variables
    prompt = tool_config["prompt"].format(
        content=content,
        target_language=target_language or "English",
        target_tone=target_tone or "professional",
    )
    prompt += platform_context

    ai_result = await _call_ai(prompt, system_prompt)

    if not ai_result:
        # Placeholder when AI unavailable
        placeholder_map = {
            "rewrite": f"[Rewritten Content]\n\n{content[:300]}...",
            "expand": f"[Expanded Content]\n\n{content}\n\n[Additional details and examples would be generated here]",
            "summarize": f"[Summary]\n\nKey points from the content above.",
            "translate": f"[Translated to {target_language or 'target language'}]\n\n{content[:200]}...",
            "improve-grammar": f"[Grammar-Improved]\n\n{content}",
            "generate-hooks": "1. 🪝 Did you know this about [topic]?\n2. 🪝 I tried [thing] for 30 days. Here's what happened.\n3. 🪝 Stop doing this common [industry] mistake.\n4. 🪝 The truth about [topic] nobody talks about.\n5. 🪝 [Statistic] of people get this wrong.",
            "generate-ctas": "1. 💬 What's your experience with this? Share below!\n2. 🚀 Ready to level up? Link in bio.\n3. ❤️ If this helped, share with someone who needs it.\n4. 📩 DM me 'START' for a free guide.\n5. 🔔 Follow for more [industry] insights.",
            "generate-hashtags": "#Industry #ProfessionalGrowth #Tips #Innovation #Trending #HowTo #BusinessTips #Learning #Strategy #Expertise #ContentCreator #SocialMedia #Marketing",
            "seo-optimize": f"[SEO-Optimized Content]\n\n{content}\n\n[Would add meta description, heading optimization, and keyword placement]",
            "tone-adjust": f"[{target_tone or 'adjusted'} Tone]\n\n{content[:300]}...",
        }
        ai_result = placeholder_map.get(tool, f"[{tool} result]\n\n{content[:300]}...")

    # Generate suggestions for certain tools
    suggestions = None
    if tool in ("generate-hooks", "generate-ctas", "generate-hashtags"):
        suggestions = [
            "Test different variations to see what resonates",
            "A/B test hooks in your first 24 hours",
            "Track engagement to refine your approach",
        ]

    return {
        "result": ai_result,
        "tool": tool,
        "suggestions": suggestions,
    }
