"""Prompt Auto-Evolver — LLM-driven prompt improvement.

After enough usage data accumulates, this service:
  1. Analyzes the current prompt's performance
  2. Gathers usage patterns (what topics worked, what didn't)
  3. Asks an LLM to suggest prompt improvements
  4. Creates a new prompt version from the suggestion

This closes the self-improvement loop:
  generate → measure → analyze → improve → generate (better)
"""
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prompt_versions import PromptVersion, PromptUsageLog
from app.services.llm import call_llm_json
from app.services.prompt_evolution import create_prompt_version

logger = logging.getLogger(__name__)

# Minimum uses before auto-evolution is allowed
MIN_USES_FOR_EVOLUTION = 3

# Minimum performance score delta to justify a new version
MIN_IMPROVEMENT_THRESHOLD = 5.0

# System prompt for the evolution LLM
_EVOLUTION_SYSTEM_PROMPT = """You are a prompt engineering expert. Your job is to improve social media content generation prompts based on performance data.

You will receive:
- The current prompt (system + user template)
- Performance score and engagement rate
- Usage history with topics and engagement outcomes
- Specific suggestions from the data analysis

Your task:
1. Analyze what's working and what's not
2. Suggest specific, actionable improvements to the system_prompt and/or user_prompt_template
3. Keep the same template variables ({topic}, {platform}, {tone}, etc.)
4. Output ONLY valid JSON with the improved prompts

Output schema:
{
  "system_prompt": "improved system prompt",
  "user_prompt_template": "improved user prompt template",
  "changes_made": ["list of specific changes you made and why"],
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation of why these changes should improve performance"
}"""


async def analyze_prompt_performance(
    db: AsyncSession,
    content_type: str,
    platform: str,
) -> dict[str, Any]:
    """Gather performance data for a prompt to feed into the evolution LLM.

    Returns a dict with:
      - current_prompt: the active prompt's system + user template
      - performance: score, usage count, engagement rate
      - usage_history: recent topics and their engagement outcomes
      - version_history: all versions and their scores
      - analysis: computed insights (best/worst topics, trends)
    """
    # Get current active prompt
    result = await db.execute(
        select(PromptVersion)
        .where(
            PromptVersion.content_type == content_type,
            PromptVersion.platform == platform,
            PromptVersion.is_active == True,
        )
    )
    current = result.scalar_one_or_none()
    if not current:
        return {"error": "No active prompt found"}

    # Get usage logs for this prompt
    logs_result = await db.execute(
        select(PromptUsageLog)
        .where(PromptUsageLog.prompt_version_id == current.id)
        .order_by(PromptUsageLog.created_at.desc())
        .limit(50)
    )
    logs = logs_result.scalars().all()

    # Get all versions for this content_type + platform
    versions_result = await db.execute(
        select(PromptVersion)
        .where(
            PromptVersion.content_type == content_type,
            PromptVersion.platform == platform,
        )
        .order_by(PromptVersion.version.desc())
    )
    versions = versions_result.scalars().all()

    # Analyze usage patterns
    scored_logs = [l for l in logs if l.actual_engagement_rate is not None]
    topics = [l.topic for l in logs if l.topic]

    best_engagement = max((l.actual_engagement_rate for l in scored_logs), default=0)
    worst_engagement = min((l.actual_engagement_rate for l in scored_logs), default=0)
    avg_engagement = (
        sum(l.actual_engagement_rate for l in scored_logs) / len(scored_logs)
        if scored_logs else 0
    )

    # Find high and low performing topics
    high_performers = [
        {"topic": l.topic, "engagement": l.actual_engagement_rate}
        for l in scored_logs
        if l.actual_engagement_rate and l.actual_engagement_rate > avg_engagement * 1.2
    ][:5]

    low_performers = [
        {"topic": l.topic, "engagement": l.actual_engagement_rate}
        for l in scored_logs
        if l.actual_engagement_rate and l.actual_engagement_rate < avg_engagement * 0.8
    ][:5]

    return {
        "current_prompt": {
            "system_prompt": current.system_prompt,
            "user_prompt_template": current.user_prompt_template,
            "version": current.version,
            "temperature": current.temperature,
        },
        "performance": {
            "score": current.performance_score,
            "usage_count": current.usage_count or 0,
            "avg_engagement_rate": round(avg_engagement, 2),
            "best_engagement": round(best_engagement, 2),
            "worst_engagement": round(worst_engagement, 2),
            "scored_uses": len(scored_logs),
        },
        "usage_history": {
            "total_uses": len(logs),
            "unique_topics": len(set(topics)),
            "high_performers": high_performers,
            "low_performers": low_performers,
            "recent_topics": topics[:10],
        },
        "version_history": [
            {
                "version": v.version,
                "score": v.performance_score,
                "uses": v.usage_count or 0,
                "created_by": v.created_by,
                "notes": v.notes,
            }
            for v in versions
        ],
    }


async def suggest_prompt_improvements(
    db: AsyncSession,
    content_type: str,
    platform: str,
    provider: str = "openai",
    model: str | None = None,
) -> dict[str, Any]:
    """Use an LLM to suggest prompt improvements based on performance data.

    Returns:
        {
            "analysis": {...},           # raw performance data
            "suggestion": {...},         # LLM suggestion
            "auto_applied": bool,        # whether a new version was created
            "new_version_id": str|None,  # ID of new version if created
        }
    """
    # Step 1: Gather performance data
    analysis = await analyze_prompt_performance(db, content_type, platform)
    if "error" in analysis:
        return {"error": analysis["error"], "auto_applied": False}

    perf = analysis["performance"]

    # Step 2: Check if evolution is warranted
    if perf["usage_count"] < MIN_USES_FOR_EVOLUTION:
        return {
            "analysis": analysis,
            "suggestion": None,
            "auto_applied": False,
            "reason": f"Only {perf['usage_count']} uses — need at least {MIN_USES_FOR_EVOLUTION} before auto-evolution",
        }

    if perf["scored_uses"] < 2:
        return {
            "analysis": analysis,
            "suggestion": None,
            "auto_applied": False,
            "reason": f"Only {perf['scored_uses']} scored uses — need engagement data to suggest improvements",
        }

    # Step 3: Build the evolution prompt
    user_prompt = f"""Analyze this prompt's performance and suggest improvements.

Content type: {content_type}
Platform: {platform}

CURRENT PROMPT:
System: {analysis['current_prompt']['system_prompt']}
User template: {analysis['current_prompt']['user_prompt_template']}

PERFORMANCE DATA:
- Score: {perf['score']}/100
- Usage count: {perf['usage_count']}
- Avg engagement rate: {perf['avg_engagement_rate']}%
- Best engagement: {perf['best_engagement']}%
- Worst engagement: {perf['worst_engagement']}%

VERSION HISTORY:
{chr(10).join(f"  v{v['version']}: score={v['score']}, uses={v['uses']}, by={v['created_by']}" for v in analysis['version_history'])}

HIGH-PERFORMING TOPICS:
{chr(10).join(f"  - {t['topic']} ({t['engagement']}% engagement)" for t in analysis['usage_history']['high_performers']) or '  None yet'}

LOW-PERFORMING TOPICS:
{chr(10).join(f"  - {t['topic']} ({t['engagement']}% engagement)" for t in analysis['usage_history']['low_performers']) or '  None yet'}

Based on this data, suggest specific improvements to the system_prompt and/or user_prompt_template that should improve engagement. Focus on:
1. What the high-performing topics have in common
2. What the low-performing topics lack
3. Specific prompt engineering techniques (few-shot examples, constraint tightening, role refinement)
4. Keep all template variables ({{topic}}, {{platform}}, etc.) intact

Output ONLY valid JSON."""

    # Step 4: Call LLM for suggestions
    suggestion = await call_llm_json(
        prompt=user_prompt,
        system_prompt=_EVOLUTION_SYSTEM_PROMPT,
        provider=provider,
        model=model,
        temperature=0.5,  # lower temp for more focused suggestions
        max_tokens=2000,
    )

    if not suggestion or not isinstance(suggestion, dict):
        return {
            "analysis": analysis,
            "suggestion": None,
            "auto_applied": False,
            "reason": "LLM failed to generate a valid suggestion",
        }

    # Step 5: Validate the suggestion
    new_system = suggestion.get("system_prompt", "")
    new_user = suggestion.get("user_prompt_template", "")
    confidence = suggestion.get("confidence", 0)

    if not new_system or not new_user:
        return {
            "analysis": analysis,
            "suggestion": suggestion,
            "auto_applied": False,
            "reason": "Suggestion missing system_prompt or user_prompt_template",
        }

    # Verify template variables are preserved
    required_vars = ["{topic}", "{platform}"]
    for var in required_vars:
        if var not in new_user:
            logger.warning("Suggestion missing required variable %s — reverting to original", var)
            new_user = analysis["current_prompt"]["user_prompt_template"]

    # Step 6: Create new prompt version
    changes = suggestion.get("changes_made", [])
    reasoning = suggestion.get("reasoning", "")
    notes = f"Auto-evolved v{analysis['current_prompt']['version']} → v{analysis['current_prompt']['version'] + 1}. Changes: {'; '.join(changes[:3])}. Reasoning: {reasoning[:200]}"

    new_pv = await create_prompt_version(
        db=db,
        content_type=content_type,
        platform=platform,
        system_prompt=new_system,
        user_prompt_template=new_user,
        created_by="auto-evolver",
        notes=notes,
        temperature=analysis["current_prompt"]["temperature"],
    )

    logger.info(
        "Auto-evolved prompt for %s/%s: v%d → v%d (confidence=%.2f)",
        content_type, platform,
        analysis["current_prompt"]["version"],
        new_pv.version,
        confidence,
    )

    return {
        "analysis": analysis,
        "suggestion": suggestion,
        "auto_applied": True,
        "new_version_id": new_pv.id,
        "new_version": new_pv.version,
    }
