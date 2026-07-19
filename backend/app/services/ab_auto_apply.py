"""A/B Test Auto-Apply — push winning variant to all platforms.

Extends A/B testing by automatically applying the winning variant
across all target platforms after test completion.
"""
import logging
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post_platform import PostPlatform

logger = logging.getLogger(__name__)


async def auto_apply_winner(
    db: AsyncSession,
    test_id: str,
    winner_variant_id: str,
    target_platforms: list[str] | None = None,
) -> dict[str, Any]:
    """Apply the winning variant across all target platforms.

    Creates new PostPlatform entries for each target platform
    using the winning variant's content.
    """
    # Get the winning variant
    result = await db.execute(
        select(PostPlatform).where(PostPlatform.id == winner_variant_id)
    )
    winner = result.scalar_one_none()
    if not winner:
        return {"error": f"Variant {winner_variant_id} not found"}

    # Get the winning content
    winning_caption = winner.caption
    winning_media = winner.media_asset_ids or []

    # Find all platforms that were part of the test
    test_result = await db.execute(
        select(PostPlatform).where(
            PostPlatform.meta["ab_test_id"].astext == test_id,
        )
    )
    test_variants = test_result.scalars().all()

    # Get unique platforms from test
    tested_platforms = list(set(v.platform for v in test_variants))
    apply_to = target_platforms or tested_platforms

    # Apply winning content to each target platform
    applied = []
    for platform in apply_to:
        if platform == winner.platform:
            continue  # Skip the winner's own platform

        # Create new PostPlatform entry with winning content
        new_pp = PostPlatform(
            post_id=winner.post_id,
            workspace_id=winner.workspace_id,
            platform=platform,
            caption=winning_caption,
            media_asset_ids=winning_media,
            status="draft",
            meta={
                "source": "ab_test_auto_apply",
                "test_id": test_id,
                "winner_variant_id": winner_variant_id,
                "applied_at": datetime.utcnow().isoformat(),
            },
        )
        db.add(new_pp)
        applied.append(platform)

    await db.flush()

    return {
        "test_id": test_id,
        "winner_variant_id": winner_variant_id,
        "applied_to": applied,
        "count": len(applied),
        "message": f"Applied winning content to {len(applied)} platform(s)",
    }
