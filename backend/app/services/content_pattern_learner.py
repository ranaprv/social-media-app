"""Content Pattern Learner — extract winning patterns from published posts.

Analyzes historical post performance to find what works, then generates
a "learning context" string that gets injected into future generation prompts.

This closes the feedback loop:
  publish → measure → extract patterns → inject into prompts → generate better

Design:
    - Analyzes top 20% vs bottom 20% posts by engagement rate
    - Extracts: hook styles, CTA patterns, content structure, hashtags, posting times
    - Generates a concise "learning context" for prompt injection
    - Caches results per workspace (refreshed when new analytics arrive)
"""
import logging
import re
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post, AnalyticsMetric

logger = logging.getLogger(__name__)

# Minimum posts needed for pattern analysis
MIN_POSTS_FOR_ANALYSIS = 5


async def extract_winning_patterns(
    db: AsyncSession,
    workspace_id: str,
    platform: str | None = None,
    days: int = 90,
) -> dict[str, Any]:
    """Analyze published posts and extract patterns from top performers.

    Returns:
        {
            "hook_patterns": [...],        # what opening lines work
            "cta_patterns": [...],          # what CTAs drive engagement
            "content_structures": [...],    # paragraph count, line breaks, etc.
            "hashtag_insights": {...},      # which hashtags correlate with engagement
            "timing_insights": {...},       # best posting times
            "length_insights": {...},       # optimal caption lengths
            "media_insights": {...},        # media vs text-only performance
            "avoid_patterns": [...],        # what top performers DON'T do
            "learning_context": "...",      # ready-to-inject context string
        }
    """
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Fetch published posts with analytics
    query = (
        select(
            Post.id,
            Post.title,
            Post.content,
            Post.platform,
            Post.published_at,
            Post.media_urls,
            func.coalesce(AnalyticsMetric.engagement, 0),
            func.coalesce(AnalyticsMetric.impressions, 0),
            func.coalesce(AnalyticsMetric.likes, 0),
            func.coalesce(AnalyticsMetric.comments, 0),
            func.coalesce(AnalyticsMetric.shares, 0),
            func.coalesce(AnalyticsMetric.clicks, 0),
        )
        .join(AnalyticsMetric, Post.id == AnalyticsMetric.post_id, isouter=True)
        .where(
            Post.workspace_id == workspace_id,
            Post.status == "published",
            Post.published_at >= cutoff,
        )
    )

    if platform:
        query = query.where(Post.platform == platform)

    query = query.order_by(Post.published_at.desc())
    rows = (await db.execute(query)).all()

    if len(rows) < MIN_POSTS_FOR_ANALYSIS:
        return {
            "hook_patterns": [],
            "cta_patterns": [],
            "content_structures": [],
            "hashtag_insights": {},
            "timing_insights": {},
            "length_insights": {},
            "media_insights": {},
            "avoid_patterns": [],
            "learning_context": "",
            "stats": {"total_posts": len(rows), "min_required": MIN_POSTS_FOR_ANALYSIS},
        }

    # Calculate engagement rates
    scored = []
    for row in rows:
        content = row[2] or ""
        impressions = row[7] or 0
        engagement = row[6] or 0
        eng_rate = (engagement / impressions * 100) if impressions > 0 else 0
        scored.append({
            "id": row[0],
            "content": content,
            "platform": row[3],
            "published_at": row[4],
            "media_urls": row[5] or [],
            "engagement": engagement,
            "impressions": impressions,
            "likes": row[8] or 0,
            "comments": row[9] or 0,
            "shares": row[10] or 0,
            "clicks": row[11] or 0,
            "eng_rate": eng_rate,
        })

    # Sort by engagement rate
    scored.sort(key=lambda x: x["eng_rate"], reverse=True)

    top_20_pct = scored[:max(1, len(scored) // 5)]
    bottom_20_pct = scored[-max(1, len(scored) // 5):]

    # Extract patterns
    hook_patterns = _extract_hook_patterns(top_20_pct)
    cta_patterns = _extract_cta_patterns(top_20_pct)
    content_structures = _extract_content_structures(top_20_pct)
    avoid_patterns = _extract_avoid_patterns(bottom_20_pct, top_20_pct)
    length_insights = _extract_length_insights(scored)
    media_insights = _extract_media_insights(scored)
    timing_insights = _extract_timing_insights(scored)

    # Generate learning context string
    learning_context = _build_learning_context(
        hook_patterns=hook_patterns,
        cta_patterns=cta_patterns,
        content_structures=content_structures,
        avoid_patterns=avoid_patterns,
        length_insights=length_insights,
        media_insights=media_insights,
        timing_insights=timing_insights,
        top_count=len(top_20_pct),
        total_count=len(scored),
    )

    return {
        "hook_patterns": hook_patterns,
        "cta_patterns": cta_patterns,
        "content_structures": content_structures,
        "hashtag_insights": {},
        "timing_insights": timing_insights,
        "length_insights": length_insights,
        "media_insights": media_insights,
        "avoid_patterns": avoid_patterns,
        "learning_context": learning_context,
        "stats": {
            "total_posts": len(scored),
            "analyzed_top": len(top_20_pct),
            "analyzed_bottom": len(bottom_20_pct),
            "period_days": days,
        },
    }


def _extract_hook_patterns(posts: list[dict]) -> list[dict]:
    """Extract hook patterns from top-performing posts."""
    patterns = []
    for post in posts:
        content = post["content"]
        if not content:
            continue
        # Get first line (the hook)
        first_line = content.strip().split("\n")[0][:200]
        if not first_line:
            continue

        # Classify hook type
        hook_type = "statement"
        if "?" in first_line:
            hook_type = "question"
        elif any(w in first_line.lower() for w in ["stop", "don't", "never", "always", "secret", "truth", "nobody"]):
            hook_type = "contrarian"
        elif any(c.isdigit() for c in first_line[:30]):
            hook_type = "number"
        elif any(w in first_line.lower() for w in ["i ", "we ", "my ", "our ", "when i"]):
            hook_type = "personal"
        elif first_line.endswith("!"):
            hook_type = "exclamation"

        patterns.append({
            "text": first_line,
            "type": hook_type,
            "eng_rate": post["eng_rate"],
            "platform": post["platform"],
        })

    # Deduplicate by type and rank by engagement
    type_best = {}
    for p in patterns:
        t = p["type"]
        if t not in type_best or p["eng_rate"] > type_best[t]["eng_rate"]:
            type_best[t] = p

    return sorted(type_best.values(), key=lambda x: x["eng_rate"], reverse=True)[:5]


def _extract_cta_patterns(posts: list[dict]) -> list[dict]:
    """Extract CTA patterns from top-performing posts."""
    cta_words = [
        "comment", "share", "save", "follow", "subscribe", "click",
        "link in bio", "drop a", "tell me", "what do you think",
        "double tap", "tag a friend", "swipe up", "check out",
    ]

    patterns = []
    for post in posts:
        content = (post["content"] or "").lower()
        for cta in cta_words:
            if cta in content:
                # Extract the sentence containing the CTA
                sentences = re.split(r'[.!?]+', post["content"] or "")
                for sent in sentences:
                    if cta in sent.lower():
                        patterns.append({
                            "text": sent.strip()[:150],
                            "cta_type": cta,
                            "eng_rate": post["eng_rate"],
                        })
                        break
                break

    # Deduplicate and rank
    seen = set()
    unique = []
    for p in patterns:
        key = p["cta_type"]
        if key not in seen:
            seen.add(key)
            unique.append(p)

    return sorted(unique, key=lambda x: x["eng_rate"], reverse=True)[:5]


def _extract_content_structures(posts: list[dict]) -> list[dict]:
    """Extract content structure patterns from top performers."""
    structures = []
    for post in posts:
        content = post["content"] or ""
        lines = content.split("\n")
        word_count = len(content.split())
        has_line_breaks = len(lines) > 1
        has_emoji = any(ord(c) > 0x1F600 for c in content)
        has_numbers = bool(re.search(r'\d+[\.\)]', content))
        has_list = bool(re.search(r'^[\s]*[-•*]\s', content, re.MULTILINE))
        para_count = len([l for l in lines if l.strip()])

        structures.append({
            "word_count": word_count,
            "line_count": len(lines),
            "has_line_breaks": has_line_breaks,
            "has_emoji": has_emoji,
            "has_numbers": has_numbers,
            "has_list": has_list,
            "paragraph_count": para_count,
            "eng_rate": post["eng_rate"],
        })

    if not structures:
        return []

    # Find average structure of top performers
    avg_words = sum(s["word_count"] for s in structures) / len(structures)
    emoji_pct = sum(1 for s in structures if s["has_emoji"]) / len(structures) * 100
    list_pct = sum(1 for s in structures if s["has_list"]) / len(structures) * 100
    line_break_pct = sum(1 for s in structures if s["has_line_breaks"]) / len(structures) * 100

    return [{
        "avg_word_count": round(avg_words),
        "emoji_usage_pct": round(emoji_pct),
        "list_usage_pct": round(list_pct),
        "line_break_usage_pct": round(line_break_pct),
    }]


def _extract_avoid_patterns(bottom_posts: list[dict], top_posts: list[dict]) -> list[str]:
    """Find patterns in bottom performers that top performers avoid."""
    avoid = []

    # Check for generic buzzwords in bottom but not top
    buzzwords = ["amazing", "incredible", "best", "ultimate", "secret", "hack", "crush", "dominate"]
    bottom_buzz = sum(1 for p in bottom_posts if any(w in (p["content"] or "").lower() for w in buzzwords))
    top_buzz = sum(1 for p in top_posts if any(w in (p["content"] or "").lower() for w in buzzwords))

    if bottom_buzz > top_buzz and bottom_posts:
        avoid.append("Generic buzzwords (amazing, incredible, best, ultimate) — bottom performers overuse these")

    # Check for walls of text
    bottom_walls = sum(1 for p in bottom_posts if len((p["content"] or "").split("\n")) <= 2 and len(p["content"] or "") > 300)
    if bottom_walls > len(bottom_posts) * 0.3:
        avoid.append("Long paragraphs without line breaks — top performers use short paragraphs")

    # Check for missing CTAs
    cta_words = ["comment", "share", "save", "follow", "think", "drop"]
    bottom_no_cta = sum(1 for p in bottom_posts if not any(w in (p["content"] or "").lower() for w in cta_words))
    if bottom_no_cta > len(bottom_posts) * 0.4:
        avoid.append("Missing call-to-action — top performers always include a CTA")

    return avoid


def _extract_length_insights(posts: list[dict]) -> dict:
    """Find optimal content length."""
    buckets = {"short (<50)": [], "medium (50-200)": [], "long (200-500)": [], "very_long (500+)": []}
    for post in posts:
        content = post["content"] or ""
        length = len(content)
        if length < 50:
            buckets["short (<50)"].append(post["eng_rate"])
        elif length < 200:
            buckets["medium (50-200)"].append(post["eng_rate"])
        elif length < 500:
            buckets["long (200-500)"].append(post["eng_rate"])
        else:
            buckets["very_long (500+)"].append(post["eng_rate"])

    avgs = {k: (sum(v) / len(v) if v else 0) for k, v in buckets.items()}
    best = max(avgs, key=avgs.get) if avgs else "medium (50-200)"

    return {
        "optimal_range": best,
        "averages": {k: round(v, 2) for k, v in avgs.items()},
    }


def _extract_media_insights(posts: list[dict]) -> dict:
    """Media vs text-only performance."""
    with_media = [p["eng_rate"] for p in posts if p.get("media_urls")]
    without_media = [p["eng_rate"] for p in posts if not p.get("media_urls")]

    avg_with = sum(with_media) / len(with_media) if with_media else 0
    avg_without = sum(without_media) / len(without_media) if without_media else 0

    return {
        "with_media_avg": round(avg_with, 2),
        "without_media_avg": round(avg_without, 2),
        "media_boost_pct": round((avg_with - avg_without) / max(avg_without, 0.1) * 100) if avg_without > 0 else 0,
        "media_usage_pct": round(len(with_media) / max(len(posts), 1) * 100),
    }


def _extract_timing_insights(posts: list[dict]) -> dict:
    """Best posting times."""
    hour_eng: dict[int, list[float]] = {}
    for post in posts:
        if post["published_at"]:
            hour = post["published_at"].hour
            if hour not in hour_eng:
                hour_eng[hour] = []
            hour_eng[hour].append(post["eng_rate"])

    avgs = {h: sum(v) / len(v) for h, v in hour_eng.items() if len(v) >= 2}
    best_hour = max(avgs, key=avgs.get) if avgs else None

    return {
        "best_hour": best_hour,
        "hour_averages": {f"{h}:00": round(v, 2) for h, v in sorted(avgs.items())},
    }


def _build_learning_context(
    hook_patterns: list[dict],
    cta_patterns: list[dict],
    content_structures: list[dict],
    avoid_patterns: list[str],
    length_insights: dict,
    media_insights: dict,
    timing_insights: dict,
    top_count: int,
    total_count: int,
) -> str:
    """Build a concise learning context string for prompt injection."""
    parts = [
        f"LEARNING FROM {top_count} TOP-PERFORMING POSTS (out of {total_count} total):",
        "",
    ]

    # Hook patterns
    if hook_patterns:
        parts.append("WORKING HOOK STYLES (from highest engagement):")
        for hp in hook_patterns[:3]:
            parts.append(f"  - {hp['type']}: \"{hp['text'][:80]}...\" ({hp['eng_rate']:.1f}% engagement)")
        parts.append("")

    # CTA patterns
    if cta_patterns:
        parts.append("WORKING CTAs:")
        for cp in cta_patterns[:3]:
            parts.append(f"  - {cp['cta_type']}: \"{cp['text'][:80]}...\"")
        parts.append("")

    # Structure
    if content_structures:
        s = content_structures[0]
        parts.append(f"OPTIMAL STRUCTURE: ~{s['avg_word_count']} words, "
                      f"{'use' if s['emoji_usage_pct'] > 50 else 'optional'} emojis, "
                      f"{'use' if s['line_break_usage_pct'] > 50 else 'add'} line breaks, "
                      f"{'include' if s['list_usage_pct'] > 30 else 'consider'} numbered lists")
        parts.append("")

    # Length
    if length_insights.get("optimal_range"):
        parts.append(f"OPTIMAL LENGTH: {length_insights['optimal_range']}")
        parts.append("")

    # Avoid
    if avoid_patterns:
        parts.append("AVOID (patterns that correlate with low engagement):")
        for ap in avoid_patterns:
            parts.append(f"  - {ap}")
        parts.append("")

    # Media
    if media_insights.get("media_boost_pct", 0) > 10:
        parts.append(f"MEDIA IMPACT: Posts with media get {media_insights['media_boost_pct']}% more engagement")
        parts.append("")

    # Timing
    if timing_insights.get("best_hour") is not None:
        parts.append(f"BEST POSTING TIME: {timing_insights['best_hour']}:00")
        parts.append("")

    parts.append("Apply these patterns to generate higher-performing content.")

    return "\n".join(parts)
