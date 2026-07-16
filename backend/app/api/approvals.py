"""Multi-Tier Approval Workflows — configurable approval chains."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("/workflows")
async def list_workflows(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """List approval workflows."""
    workflows = [
        {
            "id": "wf-1", "name": "Standard 2-Tier", "is_default": True,
            "stages": [
                {"stage": 1, "name": "Content Review", "approver_role": "editor", "required_approvals": 1},
                {"stage": 2, "name": "Final Approval", "approver_role": "admin", "required_approvals": 1},
            ],
        },
        {
            "id": "wf-2", "name": "Enterprise 3-Tier", "is_default": False,
            "stages": [
                {"stage": 1, "name": "Editor Review", "approver_role": "editor", "required_approvals": 1},
                {"stage": 2, "name": "Compliance Check", "approver_role": "admin", "required_approvals": 1},
                {"stage": 3, "name": "Brand Approval", "approver_role": "owner", "required_approvals": 1},
            ],
        },
    ]
    return {"workflows": workflows}


@router.post("/workflows")
async def create_workflow(request: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Create an approval workflow."""
    stages = request.get("stages", [])
    for i, stage in enumerate(stages):
        stage["stage"] = i + 1
    return {
        "id": str(uuid.uuid4()),
        "name": request.get("name", "New Workflow"),
        "stages": stages,
        "is_default": False,
        "created_at": datetime.utcnow().isoformat(),
    }


@router.get("/pending")
async def list_pending_approvals(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """List posts awaiting approval."""
    pending = [
        {"id": "ap-1", "post_id": "post-5", "post_title": "Product Update: New Features", "workflow_name": "Standard 2-Tier", "current_stage": 1, "total_stages": 2, "stage_name": "Content Review", "requested_by": "Sarah Chen", "requested_at": "2026-07-15T10:00:00"},
        {"id": "ap-2", "post_id": "post-7", "post_title": "Behind the Scenes Reel", "workflow_name": "Enterprise 3-Tier", "current_stage": 2, "total_stages": 3, "stage_name": "Compliance Check", "requested_by": "Marcus Johnson", "requested_at": "2026-07-14T14:00:00"},
    ]
    return {"approvals": pending, "total": len(pending)}


@router.post("/approve/{approval_id}")
async def approve(approval_id: str, request: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Approve at current stage."""
    comment = request.get("comment", "")
    return {"id": approval_id, "status": "approved", "message": "Approved at current stage", "next_stage": 2}


@router.post("/reject/{approval_id}")
async def reject(approval_id: str, request: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Reject and request changes."""
    reason = request.get("reason", "")
    return {"id": approval_id, "status": "rejected", "reason": reason, "message": "Changes requested"}
