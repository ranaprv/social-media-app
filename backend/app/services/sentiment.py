"""AI Sentiment Analysis service."""
import logging
from app.services.llm import call_llm_json

logger = logging.getLogger(__name__)


async def analyze_sentiment(text: str, provider: str = "openai", model: str = None) -> dict:
    """Analyze text sentiment using AI. Returns sentiment + score."""
    system_prompt = """Analyze the sentiment of the given text. Return JSON with:
- "sentiment": "positive" | "negative" | "neutral"
- "score": float between 0.0 and 1.0 (0=negative, 0.5=neutral, 1=positive)
- "confidence": float between 0.0 and 1.0
- "keywords": array of sentiment-driving words
Return ONLY valid JSON."""

    result = await call_llm_json(text, system_prompt, provider=provider, model=model or "gpt-4o-mini", temperature=0.3)

    if result and isinstance(result, dict):
        return {
            "sentiment": result.get("sentiment", "neutral"),
            "score": float(result.get("score", 0.5)),
            "confidence": float(result.get("confidence", 0.5)),
            "keywords": result.get("keywords", []),
        }

    # Fallback: simple keyword-based sentiment
    positive_words = {"great", "love", "amazing", "excellent", "good", "best", "awesome", "fantastic", "helpful", "insightful", "thanks", "congratulations", "perfect"}
    negative_words = {"bad", "terrible", "worst", "hate", "awful", "disappointing", "poor", "boring", "useless", "frustrating", "annoying", "fail"}

    words = set(text.lower().split())
    pos_count = len(words & positive_words)
    neg_count = len(words & negative_words)
    total = pos_count + neg_count

    if total == 0:
        return {"sentiment": "neutral", "score": 0.5, "confidence": 0.3, "keywords": []}

    score = pos_count / total
    return {
        "sentiment": "positive" if score > 0.6 else "negative" if score < 0.4 else "neutral",
        "score": score,
        "confidence": min(total / 5, 1.0),
        "keywords": list((words & positive_words) | (words & negative_words)),
    }
