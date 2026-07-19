"""Batch operations helper — efficient bulk database operations.

Uses SQLAlchemy bulk operations to avoid N+1 queries in bulk updates.
"""
import logging
from typing import Any, Sequence

from sqlalchemy import update, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def bulk_update(
    db: AsyncSession,
    model: Any,
    ids: Sequence[str],
    values: dict[str, Any],
    batch_size: int = 100,
) -> int:
    """Update multiple rows efficiently using bulk operations.

    Args:
        db: AsyncSession
        model: SQLAlchemy model class
        ids: List of primary key values
        values: Dict of column=value to set
        batch_size: Number of rows per batch (for very large updates)

    Returns:
        Number of rows updated
    """
    if not ids:
        return 0

    total_updated = 0

    # Process in batches to avoid memory issues
    for i in range(0, len(ids), batch_size):
        batch = ids[i:i + batch_size]

        result = await db.execute(
            update(model)
            .where(model.id.in_(batch))
            .values(**values)
        )
        total_updated += result.rowcount

    logger.info(f"Bulk updated {total_updated} {model.__name__} rows")
    return total_updated


async def bulk_update_status(
    db: AsyncSession,
    model: Any,
    ids: Sequence[str],
    new_status: str,
    extra_values: dict[str, Any] | None = None,
) -> int:
    """Bulk update status field with optional extra values."""
    values = {"status": new_status}
    if extra_values:
        values.update(extra_values)
    return await bulk_update(db, model, ids, values)


async def bulk_delete(
    db: AsyncSession,
    model: Any,
    ids: Sequence[str],
    batch_size: int = 100,
) -> int:
    """Delete multiple rows efficiently."""
    if not ids:
        return 0

    total_deleted = 0

    for i in range(0, len(ids), batch_size):
        batch = ids[i:i + batch_size]

        result = await db.execute(
            delete(model).where(model.id.in_(batch))
        )
        total_deleted += result.rowcount

    logger.info(f"Bulk deleted {total_deleted} {model.__name__} rows")
    return total_deleted


async def bulk_upsert(
    db: AsyncSession,
    model: Any,
    items: list[dict[str, Any]],
    unique_key: str = "id",
    batch_size: int = 100,
) -> int:
    """Insert or update multiple rows.

    For each item, if the unique_key exists, update; otherwise insert.
    """
    if not items:
        return 0

    count = 0

    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]

        # Get existing IDs
        ids = [item[unique_key] for item in batch if unique_key in item]
        if ids:
            existing_result = await db.execute(
                select(model.id).where(model.id.in_(ids))
            )
            existing_ids = set(row[0] for row in existing_result.all())
        else:
            existing_ids = set()

        for item in batch:
            item_id = item.get(unique_key)
            if item_id in existing_ids:
                # Update
                await db.execute(
                    update(model)
                    .where(model.id == item_id)
                    .values(**{k: v for k, v in item.items() if k != unique_key})
                )
            else:
                # Insert
                db.add(model(**item))
            count += 1

    logger.info(f"Bulk upserted {count} {model.__name__} rows")
    return count


async def count_by_status(
    db: AsyncSession,
    model: Any,
    workspace_id: str | None = None,
    filters: dict[str, Any] | None = None,
) -> dict[str, int]:
    """Count rows grouped by status field."""
    from sqlalchemy import func

    query = select(model.status, func.count(model.id))

    if workspace_id and hasattr(model, "workspace_id"):
        query = query.where(model.workspace_id == workspace_id)

    if filters:
        for col_name, value in filters.items():
            if hasattr(model, col_name):
                col = getattr(model, col_name)
                query = query.where(col == value)

    query = query.group_by(model.status)
    result = await db.execute(query)

    return {row[0]: row[1] for row in result.all()}
