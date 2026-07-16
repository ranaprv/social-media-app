"""Task Assignment & Routing — CRUD tasks, routing rules."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("")
async def list_tasks(
    status: str = None,
    assigned_to: str = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List tasks with filtering."""
    now = datetime.utcnow()
    tasks = [
        {"id": "t-1", "title": "Reply to Sarah's collaboration inquiry", "description": "She wants to discuss a guest post partnership", "assigned_to": "current_user", "assigned_by": "auto-router", "status": "open", "priority": "high", "due_date": (now + timedelta(days=2)).isoformat(), "source_message_id": "m-1", "created_at": (now - timedelta(hours=2)).isoformat()},
        {"id": "t-2", "title": "Review negative mention on Instagram", "description": "User expressing frustration about social media tools", "assigned_to": "current_user", "assigned_by": "auto-router", "status": "in_progress", "priority": "medium", "due_date": (now + timedelta(days=1)).isoformat(), "source_message_id": "m-3", "created_at": (now - timedelta(hours=5)).isoformat()},
        {"id": "t-3", "title": "Follow up on YouTube comment", "description": "Positive comment on content strategy video", "assigned_to": "current_user", "assigned_by": "manual", "status": "resolved", "priority": "low", "due_date": None, "source_message_id": "m-5", "created_at": (now - timedelta(days=1)).isoformat()},
    ]
    if status:
        tasks = [t for t in tasks if t["status"] == status]
    return {"tasks": tasks, "total": len(tasks)}


@router.post("")
async def create_task(request: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Create a new task."""
    return {
        "id": str(uuid.uuid4()),
        "title": request.get("title", ""),
        "description": request.get("description", ""),
        "assigned_to": request.get("assigned_to", current_user.id),
        "assigned_by": current_user.id,
        "status": "open",
        "priority": request.get("priority", "medium"),
        "due_date": request.get("due_date"),
        "source_message_id": request.get("source_message_id"),
        "created_at": datetime.utcnow().isoformat(),
    }


@router.put("/{task_id}")
async def update_task(task_id: str, request: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Update a task."""
    return {"id": task_id, "message": "Task updated", "updates": request}


@router.put("/{task_id}/status")
async def update_task_status(task_id: str, request: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Update task status."""
    new_status = request.get("status", "open")
    return {"id": task_id, "status": new_status, "message": f"Task moved to {new_status}"}
