"""Story Arc Templates — narrative frameworks for content series.

Provides structured storytelling templates for social media content.
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)

STORY_ARCS = {
    "heros_journey": {
        "name": "Hero's Journey",
        "description": "Classic narrative arc: call to adventure → challenges → transformation → return",
        "parts": [
            {"name": "Ordinary World", "description": "Set the scene — where your audience is now", "prompt": "Describe the current state of your audience's world"},
            {"name": "Call to Adventure", "description": "Introduce the challenge or opportunity", "prompt": "What problem or opportunity are you presenting?"},
            {"name": "Challenges", "description": "Obstacles and struggles", "prompt": "What obstacles does your audience face?"},
            {"name": "Transformation", "description": "The breakthrough moment", "prompt": "What's the solution or key insight?"},
            {"name": "Return with Knowledge", "description": "Share the wisdom gained", "prompt": "What's the takeaway your audience should apply?"},
        ],
        "platforms": ["linkedin", "youtube"],
        "best_for": ["case studies", "personal stories", "product journeys"],
    },
    "problem_agitate_solve": {
        "name": "Problem-Agitate-Solve (PAS)",
        "description": "Identify problem → make it urgent → present solution",
        "parts": [
            {"name": "Problem", "description": "Name the pain point clearly", "prompt": "What specific problem does your audience face?"},
            {"name": "Agitate", "description": "Make the problem feel urgent and costly", "prompt": "What happens if they don't solve this? What's the cost?"},
            {"name": "Solve", "description": "Present your solution", "prompt": "How does your product/approach solve this?"},
        ],
        "platforms": ["linkedin", "x", "facebook"],
        "best_for": ["product launches", "pain-point content", "conversion posts"],
    },
    "before_after_bridge": {
        "name": "Before-After-Bridge (BAB)",
        "description": "Show before state → show after state → bridge the gap",
        "parts": [
            {"name": "Before", "description": "The current painful state", "prompt": "Describe the 'before' state of your audience"},
            {"name": "After", "description": "The ideal future state", "prompt": "What does life look like after the transformation?"},
            {"name": "Bridge", "description": "How to get from before to after", "prompt": "What steps or product bridges the gap?"},
        ],
        "platforms": ["linkedin", "instagram", "facebook"],
        "best_for": ["testimonials", "case studies", "before/after content"],
    },
    "star_method": {
        "name": "STAR Method",
        "description": "Situation → Task → Action → Result",
        "parts": [
            {"name": "Situation", "description": "Set the context", "prompt": "What was the situation or challenge?"},
            {"name": "Task", "description": "Define the specific task", "prompt": "What needed to be done?"},
            {"name": "Action", "description": "Describe the actions taken", "prompt": "What specific steps were taken?"},
            {"name": "Result", "description": "Share the measurable outcome", "prompt": "What was the result? Include metrics."},
        ],
        "platforms": ["linkedin", "x"],
        "best_for": ["career stories", "project recaps", "interview prep"],
    },
    "listicle_arc": {
        "name": "Listicle Arc",
        "description": "Numbered insights building to a climax",
        "parts": [
            {"name": "Hook", "description": "Number + promise", "prompt": "What's the headline promise? (e.g., '5 Ways to...')"},
            {"name": "Items", "description": "Numbered insights (3-10)", "prompt": "List your key points with brief explanations"},
            {"name": "Climax", "description": "The most powerful point", "prompt": "What's your #1 insight?"},
            {"name": "CTA", "description": "Action step for the reader", "prompt": "What should they do next?"},
        ],
        "platforms": ["linkedin", "x", "instagram"],
        "best_for": ["tips content", "how-to guides", "resource lists"],
    },
    "storytelling_hook": {
        "name": "Storytelling Hook",
        "description": "Personal story → lesson → application",
        "parts": [
            {"name": "Hook", "description": "Attention-grabbing opening", "prompt": "What's your most compelling opening line?"},
            {"name": "Story", "description": "The narrative", "prompt": "Tell the story with specific details"},
            {"name": "Lesson", "description": "The insight or lesson learned", "prompt": "What's the key takeaway?"},
            {"name": "Application", "description": "How the audience can apply it", "prompt": "How can readers use this insight?"},
        ],
        "platforms": ["linkedin", "instagram", "youtube"],
        "best_for": ["personal branding", "thought leadership", "engagement posts"],
    },
}


def get_story_arcs() -> list[dict[str, Any]]:
    """Get all available story arc templates."""
    return [
        {"key": k, "name": v["name"], "description": v["description"],
         "parts_count": len(v["parts"]), "platforms": v["platforms"], "best_for": v["best_for"]}
        for k, v in STORY_ARCS.items()
    ]


def get_story_arc(arc_key: str) -> dict[str, Any] | None:
    """Get a specific story arc template."""
    return STORY_ARCS.get(arc_key)


def get_arc_prompts(arc_key: str) -> list[dict[str, str]]:
    """Get the guiding prompts for a story arc."""
    arc = STORY_ARCS.get(arc_key)
    if not arc:
        return []
    return [{"name": p["name"], "description": p["description"], "prompt": p["prompt"]} for p in arc["parts"]]
