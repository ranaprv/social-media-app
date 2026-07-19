"""CTA Library — organized library by goal, platform, and tone.

Pre-built call-to-action templates for social media content.
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)

CTA_LIBRARY = {
    "engagement": {
        "name": "Engagement CTAs",
        "description": "Drive comments, likes, and shares",
        "ctas": [
            {"text": "What do you think? Drop your thoughts below 👇", "platforms": ["linkedin", "facebook"], "tone": "conversational"},
            {"text": "Agree or disagree? Let me know in the comments", "platforms": ["linkedin", "x"], "tone": "provocative"},
            {"text": "Tag someone who needs to see this", "platforms": ["instagram", "facebook"], "tone": "casual"},
            {"text": "Save this for later — you'll thank yourself", "platforms": ["instagram"], "tone": "helpful"},
            {"text": "Retweet if this resonates 🔄", "platforms": ["x"], "tone": "casual"},
            {"text": "Which one resonates most with you? A or B?", "platforms": ["linkedin", "x"], "tone": "engaging"},
            {"text": "Have you experienced this? Share your story below", "platforms": ["linkedin", "facebook"], "tone": "personal"},
            {"text": "Double-tap if you agree ❤️", "platforms": ["instagram"], "tone": "casual"},
        ],
    },
    "traffic": {
        "name": "Traffic CTAs",
        "description": "Drive clicks to website/blog/landing page",
        "ctas": [
            {"text": "Read the full guide → [link]", "platforms": ["linkedin", "x", "facebook"], "tone": "direct"},
            {"text": "Link in bio for the full breakdown", "platforms": ["instagram"], "tone": "casual"},
            {"text": "New blog post: [topic]. Link in comments 👇", "platforms": ["linkedin", "facebook"], "tone": "informative"},
            {"text": "Watch the full video → [link]", "platforms": ["x", "facebook"], "tone": "direct"},
            {"text": "Download the free template → [link in bio]", "platforms": ["instagram"], "tone": "value-first"},
            {"text": "Check out our latest case study → [link]", "platforms": ["linkedin", "facebook"], "tone": "professional"},
        ],
    },
    "leads": {
        "name": "Lead Generation CTAs",
        "description": "Capture emails and generate leads",
        "ctas": [
            {"text": "Get our free [resource] — link in bio", "platforms": ["instagram", "linkedin"], "tone": "value-first"},
            {"text": "Download the [guide/template/ebook] → [link]", "platforms": ["linkedin", "facebook"], "tone": "direct"},
            {"text": "Sign up for our free newsletter → [link]", "platforms": ["linkedin", "x", "facebook"], "tone": "casual"},
            {"text": "Book a free consultation → [link]", "platforms": ["linkedin", "facebook"], "tone": "professional"},
            {"text": "Start your free trial → [link in bio]", "platforms": ["instagram", "x"], "tone": "direct"},
            {"text": "Join 10,000+ [audience] — get the free toolkit → [link]", "platforms": ["linkedin", "x"], "tone": "social-proof"},
        ],
    },
    "sales": {
        "name": "Sales CTAs",
        "description": "Drive purchases and conversions",
        "ctas": [
            {"text": "Ready to [transform]? Book a demo → [link]", "platforms": ["linkedin", "facebook"], "tone": "professional"},
            {"text": "Limited offer: [deal]. Grab it before it's gone → [link]", "platforms": ["x", "instagram", "facebook"], "tone": "urgency"},
            {"text": "See how [product] can [benefit] → [link]", "platforms": ["linkedin", "facebook"], "tone": "benefit-focused"},
            {"text": "Join the waitlist → [link]", "platforms": ["instagram", "x", "linkedin"], "tone": "exclusive"},
            {"text": "Upgrade to Pro today → [link in bio]", "platforms": ["instagram", "x"], "tone": "direct"},
            {"text": "Transform your [area] in 30 days. Get started → [link]", "platforms": ["linkedin", "facebook"], "tone": "aspirational"},
        ],
    },
    "community": {
        "name": "Community CTAs",
        "description": "Build community and followers",
        "ctas": [
            {"text": "Follow for daily [topic] tips", "platforms": ["instagram", "x", "linkedin"], "tone": "value-first"},
            {"text": "Subscribe to our channel for more → [link]", "platforms": ["youtube", "x"], "tone": "casual"},
            {"text": "Join our community of [number]+ [audience]", "platforms": ["linkedin", "facebook"], "tone": "social-proof"},
            {"text": "Hit the bell 🔔 so you don't miss our next post", "platforms": ["youtube", "instagram"], "tone": "casual"},
            {"text": "Turn on post notifications to stay in the loop", "platforms": ["instagram", "facebook"], "tone": "casual"},
            {"text": "Share this with someone who'd find it useful", "platforms": ["linkedin", "x", "facebook"], "tone": "helpful"},
        ],
    },
}


def get_ctas_by_goal(goal: str) -> list[dict[str, str]]:
    """Get CTAs filtered by goal."""
    return CTA_LIBRARY.get(goal, {}).get("ctas", [])


def get_ctas_by_platform(platform: str) -> list[dict[str, str]]:
    """Get all CTAs that work on a specific platform."""
    ctas = []
    for goal_data in CTA_LIBRARY.values():
        for cta in goal_data["ctas"]:
            if platform in cta["platforms"]:
                ctas.append({**cta, "goal": goal_data["name"]})
    return ctas


def get_all_cta_goals() -> list[dict[str, str]]:
    """Get all available CTA goals."""
    return [
        {"key": k, "name": v["name"], "description": v["description"], "count": len(v["ctas"])}
        for k, v in CTA_LIBRARY.items()
    ]


def search_ctas(query: str) -> list[dict[str, Any]]:
    """Search CTAs by keyword."""
    results = []
    query_lower = query.lower()
    for goal_key, goal_data in CTA_LIBRARY.items():
        for cta in goal_data["ctas"]:
            if query_lower in cta["text"].lower() or query_lower in goal_data["name"].lower():
                results.append({**cta, "goal": goal_data["name"]})
    return results
