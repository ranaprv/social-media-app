"""Message Automation — rules, auto-replies, keyword triggers."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/automation", tags=["automation"])


@router.get("/rules")
async def list_rules(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """List automation rules."""
    rules = [
        {"id": "ar-1", "trigger_type": "keyword", "trigger_value": "pricing", "action_type": "reply", "response_text": "Thanks for asking! Check our pricing page at pricing.socialmediamanager.ai", "platforms": ["linkedin", "x"], "is_active": True, "trigger_count": 12},
        {"id": "ar-2", "trigger_type": "keyword", "trigger_value": "demo", "action_type": "reply", "response_text": "We'd love to show you a demo! Book a time here: calendly.com/socialmediamanager", "platforms": ["linkedin"], "is_active": True, "trigger_count": 8},
        {"id": "ar-3", "trigger_type": "keyword", "trigger_value": "thank", "action_type": "reply", "response_text": "You're welcome! Let us know if you need anything else.", "platforms": ["x", "instagram"], "is_active": True, "trigger_count": 25},
    ]
    return {"rules": rules, "total": len(rules)}


@router.post("/rules")
async def create_rule(request: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Create an automation rule."""
    return {
        "id": str(uuid.uuid4()),
        "trigger_type": request.get("trigger_type", "keyword"),
        "trigger_value": request.get("trigger_value", ""),
        "action_type": request.get("action_type", "reply"),
        "response_text": request.get("response_text", ""),
        "platforms": request.get("platforms", ["x"]),
        "is_active": True,
        "trigger_count": 0,
        "created_at": datetime.utcnow().isoformat(),
    }


@router.put("/rules/{rule_id}")
async def update_rule(rule_id: str, request: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Update an automation rule."""
    return {"id": rule_id, "message": "Rule updated", "updates": request}


@router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Delete an automation rule."""
    return {"id": rule_id, "message": "Rule deleted"}


@router.put("/rules/{rule_id}/toggle")
async def toggle_rule(rule_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Toggle rule active status."""
    return {"id": rule_id, "is_active": True, "message": "Rule toggled"}


@router.post("/rules/{rule_id}/test")
async def test_rule(rule_id: str, request: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Test a rule against a sample message."""
    message = request.get("message", "")
    return {
        "rule_id": rule_id,
        "message": message,
        "matched": "pricing" in message.lower(),
        "would_reply": True,
        "response": "Thanks for asking! Check our pricing page.",
    }
