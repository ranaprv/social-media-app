"""Analytics feedback loop with performance scoring and mock vector store.

Implements the normalised Performance Score:
    Ps = w1 * (Engagements / Impressions)
       + w2 * (Shares / Impressions)
       + w3 * (Clicks / Impressions)

When Ps > 7.5 the post text is embedded and stored in a simulated vector
store for future few-shot generation context.
"""
from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.schemas.ai_workflow import PerformanceScoreResponse

logger = logging.getLogger(__name__)

# ── Scoring weights (sum = 1.0) ───────────────────────────────────────────
W_ENGAGEMENT = 0.50
W_SHARES = 0.30
W_CLICKS = 0.20
HIGH_SCORE_THRESHOLD = 7.5


# ── Simulated vector store (in-memory for skeleton) ────────────────────────

@dataclass
class VectorEntry:
    """A single embedding record in the mock vector store."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    post_id: str = ""
    text: str = ""
    embedding: list[float] = field(default_factory=list)
    performance_score: float = 0.0
    stored_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)


class MockVectorStore:
    """In-memory vector store — replace with pgvector / Pinecone / Weaviate in production."""

    def __init__(self) -> None:
        self._entries: list[VectorEntry] = []

    def insert(self, entry: VectorEntry) -> None:
        self._entries.append(entry)
        logger.info(
            "Vector store: inserted entry %s (score=%.2f, text_len=%d)",
            entry.id,
            entry.performance_score,
            len(entry.text),
        )

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[VectorEntry]:
        """Cosine-similarity search (mock — returns all entries sorted by score desc)."""
        # In production: pgvector cosine distance, Pinecone query, etc.
        return sorted(self._entries, key=lambda e: e.performance_score, reverse=True)[:top_k]

    @property
    def count(self) -> int:
        return len(self._entries)


# Module-level singleton
_vector_store = MockVectorStore()


def get_vector_store() -> MockVectorStore:
    return _vector_store


# ── Mock embedding generator ──────────────────────────────────────────────

def _mock_embedding(text: str, dimensions: int = 1536) -> list[float]:
    """Generate a deterministic mock embedding from text hash.

    In production this calls ``openai.embeddings.create(model="text-embedding-3-small")``.
    """
    digest = hashlib.sha256(text.encode()).hexdigest()
    # Convert hex digest to floats in [-1, 1]
    raw = [int(digest[i : i + 2], 16) / 127.5 - 1.0 for i in range(0, min(len(digest), dimensions * 2), 2)]
    # Pad or truncate to exact dimensions
    if len(raw) < dimensions:
        raw.extend([0.0] * (dimensions - len(raw)))
    return raw[:dimensions]


# ── Performance score calculator ───────────────────────────────────────────

def calculate_performance_score(
    impressions: int,
    engagements: int,
    shares: int,
    clicks: int,
) -> tuple[float, dict[str, float]]:
    """Compute the normalised performance score Ps.

    Returns:
        (score, breakdown) where breakdown maps component names to raw ratios.
    """
    if impressions <= 0:
        return 0.0, {"engagement_rate": 0.0, "share_rate": 0.0, "click_rate": 0.0}

    eng_rate = engagements / impressions
    share_rate = shares / impressions
    click_rate = clicks / impressions

    raw_score = W_ENGAGEMENT * eng_rate + W_SHARES * share_rate + W_CLICKS * click_rate

    # Scale to 0–10 range (raw_score max is ~1.0 when all ratios are 1.0)
    score = round(min(raw_score * 10.0, 10.0), 2)

    breakdown = {
        "engagement_rate": round(eng_rate, 4),
        "share_rate": round(share_rate, 4),
        "click_rate": round(click_rate, 4),
        "w_engagement": W_ENGAGEMENT,
        "w_shares": W_SHARES,
        "w_clicks": W_CLICKS,
    }
    return score, breakdown


# ── Main feedback loop service ────────────────────────────────────────────

class AnalyticsFeedbackLoop:
    """Processes ingested analytics, computes scores, and stores high-performers as embeddings."""

    def __init__(self, vector_store: MockVectorStore | None = None) -> None:
        self._store = vector_store or get_vector_store()

    async def process_performance_and_store_rag(
        self,
        platform_post_id: str,
        post_text: str,
        *,
        impressions: int,
        engagements: int,
        shares: int,
        clicks: int,
        platform: str = "",
        recorded_at: datetime | None = None,
    ) -> PerformanceScoreResponse:
        """Calculate score and conditionally store embedding for future RAG context.

        Args:
            platform_post_id: Native platform post identifier.
            post_text: The post's text content (used for embedding when score is high).
            impressions / engagements / shares / clicks: Raw platform metrics.

        Returns:
            ``PerformanceScoreResponse`` with score and breakdown.
        """
        score, breakdown = calculate_performance_score(impressions, engagements, shares, clicks)

        stored = False
        if score > HIGH_SCORE_THRESHOLD:
            embedding = _mock_embedding(post_text)
            entry = VectorEntry(
                post_id=platform_post_id,
                text=post_text,
                embedding=embedding,
                performance_score=score,
                metadata={"platform": platform, "recorded_at": (recorded_at or datetime.now(timezone.utc)).isoformat()},
            )
            self._store.insert(entry)
            stored = True
            logger.info(
                "High-performing post %s (score=%.2f > %.1f) — stored as embedding for RAG",
                platform_post_id,
                score,
                HIGH_SCORE_THRESHOLD,
            )
        else:
            logger.info(
                "Post %s score=%.2f — below threshold %.1f, not stored",
                platform_post_id,
                score,
                HIGH_SCORE_THRESHOLD,
            )

        return PerformanceScoreResponse(
            platform_post_id=platform_post_id,
            performance_score=score,
            stored_as_embedding=stored,
            breakdown=breakdown,
        )
