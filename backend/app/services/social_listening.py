"""Social listening — brand mention monitoring.

Monitors mentions of brand, keywords, and competitors across platforms.
Provides sentiment analysis and alert triggers.
"""
import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Default listening rules
DEFAULT_LISTENING_RULES = [
    {
        "id": "rule-brand-mention",
        "name": "Brand Mentions",
        "type": "keyword",
        "keywords": [],
        "platforms": ["linkedin", "x", "instagram", "facebook"],
        "alert_on": "mention",
        "enabled": False,
    },
    {
        "id": "rule-competitor",
        "name": "Competitor Mentions",
        "type": "keyword",
        "keywords": [],
        "platforms": ["x", "linkedin"],
        "alert_on": "mention",
        "enabled": False,
    },
    {
        "id": "rule-industry",
        "name": "Industry Keywords",
        "type": "keyword",
        "keywords": [],
        "platforms": ["x", "linkedin"],
        "alert_on": "trending",
        "enabled": False,
    },
    {
        "id": "rule-sentiment",
        "name": "Negative Sentiment",
        "type": "sentiment",
        "sentiment": "negative",
        "platforms": ["x", "facebook"],
        "alert_on": "negative",
        "enabled": False,
    },
]


async def create_listening_rule(
    db: AsyncSession,
    workspace_id: str,
    name: str,
    keywords: list[str],
    platforms: list[str],
    alert_type: str = "mention",
) -> dict[str, Any]:
    """Create a social listening rule."""
    import uuid
    from app.models.content import Activity

    activity = Activity(
        id=str(uuid.uuid4()),
        user_id="system",
        type="listening_rule_created",
        description=f"Created listening rule: {name}",
        meta={
            "rule_name": name,
            "keywords": keywords,
            "platforms": platforms,
            "alert_type": alert_type,
        },
    )
    db.add(activity)
    await db.flush()

    return {
        "rule_id": str(uuid.uuid4()),
        "name": name,
        "keywords": keywords,
        "platforms": platforms,
        "alert_type": alert_type,
        "enabled": True,
    }


async def scan_mentions(
    keywords: list[str],
    platforms: list[str],
    time_window_hours: int = 24,
) -> dict[str, Any]:
    """Scan for mentions across platforms.

    In production, this would query platform APIs for mentions.
    Returns mock data structure for now.
    """
    # This is a placeholder — real implementation would call platform APIs
    mentions: list[dict[str, Any]] = []

    for platform in platforms:
        # Simulate finding mentions
        for keyword in keywords:
            mentions.append({
                "platform": platform,
                "keyword": keyword,
                "author": f"user_{platform}",
                "content": f"Mentioned {keyword} on {platform}",
                "sentiment": "neutral",
                "timestamp": datetime.utcnow().isoformat(),
                "engagement": {"likes": 0, "shares": 0, "comments": 0},
            })

    # Sentiment summary
    sentiments = {"positive": 0, "neutral": 0, "negative": 0}
    for m in mentions:
        s = m.get("sentiment", "neutral")
        sentiments[s] = sentiments.get(s, 0) + 1

    return {
        "total_mentions": len(mentions),
        "mentions": mentions[:50],
        "sentiment_summary": sentiments,
        "time_window_hours": time_window_hours,
        "platforms_scanned": platforms,
        "keywords_tracked": keywords,
    }


def get_listening_rules() -> list[dict[str, Any]]:
    """Get default listening rules."""
    return DEFAULT_LISTENING_RULES


def analyze_sentiment(text: str) -> dict[str, Any]:
    """Basic sentiment analysis using keyword matching."""
    positive_words = {"great", "amazing", "love", "excellent", "awesome", "fantastic", "wonderful", "happy", "best", "perfect", "brilliant", "outstanding"}
    negative_words = {"bad", "terrible", "hate", "awful", "worst", "horrible", "poor", "disappointing", "angry", "frustrated", "annoyed", "broken"}

    words = set(text.lower().split())
    pos_count = len(words.intersection(positive_words))
    neg_count = len(words.intersection(negative_words))

    if pos_count > neg_count:
        sentiment = "positive"
        score = min(1.0, 0.5 + (pos_count - neg_count) * 0.1)
    elif neg_count > pos_count:
        sentiment = "negative"
        score = max(-1.0, -0.5 - (neg_count - pos_count) * 0.1)
    else:
        sentiment = "neutral"
        score = 0.0

    return {
        "sentiment": sentiment,
        "score": round(score, 2),
        "positive_signals": pos_count,
        "negative_signals": neg_count,
    }
