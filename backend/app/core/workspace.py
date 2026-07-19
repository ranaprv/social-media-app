"""Shared workspace utility — ensures the system workspace exists.

Extracted to avoid duplicating workspace-creation logic across
connections.py, media.py, and other modules.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.workspace import Workspace
from app.models.user import User

SYSTEM_WORKSPACE_ID = "system-workspace"


async def ensure_system_workspace(db: AsyncSession) -> str:
    """Ensure the system workspace exists. Returns its ID.

    Uses a deterministic slug-based lookup to avoid duplicates
    from concurrent requests.
    """
    ws_result = await db.execute(
        select(Workspace).where(Workspace.id == SYSTEM_WORKSPACE_ID)
    )
    if ws_result.scalar_one_or_none():
        return SYSTEM_WORKSPACE_ID

    # Find an existing user to own the workspace
    user_result = await db.execute(select(User).limit(1))
    first_user = user_result.scalar_one_or_none()
    owner_id = first_user.id if first_user else "system-user"

    if not first_user:
        sys_user = User(id="system-user", email="system@local", name="System")
        db.add(sys_user)
        await db.flush()

    ws = Workspace(
        id=SYSTEM_WORKSPACE_ID,
        name="System",
        slug="system",
        owner_id=owner_id,
    )
    db.add(ws)
    try:
        await db.flush()
    except Exception:
        # Race: another request created it — just return the ID
        await db.rollback()

    return SYSTEM_WORKSPACE_ID
