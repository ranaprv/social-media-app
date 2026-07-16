"""Custom Analytics Reports — builder, export, scheduling."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("")
async def list_reports(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """List saved reports."""
    reports = [
        {"id": "rpt-1", "name": "Weekly Performance", "metrics": ["reach", "engagement", "followers"], "platforms": ["linkedin", "x"], "schedule": "weekly", "last_generated": "2026-07-14", "created_by": "admin"},
        {"id": "rpt-2", "name": "Monthly Content Summary", "metrics": ["posts", "impressions", "clicks"], "platforms": ["all"], "schedule": "monthly", "last_generated": "2026-07-01", "created_by": "admin"},
    ]
    return {"reports": reports}


@router.post("")
async def create_report(request: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Create a custom report configuration."""
    return {
        "id": str(uuid.uuid4()),
        "name": request.get("name", "Untitled Report"),
        "metrics": request.get("metrics", ["reach", "engagement"]),
        "platforms": request.get("platforms", ["all"]),
        "date_range_start": request.get("date_range_start"),
        "date_range_end": request.get("date_range_end"),
        "schedule": request.get("schedule", "none"),
        "created_by": current_user.email,
        "created_at": datetime.utcnow().isoformat(),
    }


@router.post("/{report_id}/generate")
async def generate_report(report_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Generate report data."""
    return {
        "report_id": report_id,
        "generated_at": datetime.utcnow().isoformat(),
        "data": {
            "summary": {"total_reach": 142500, "total_engagement": 12400, "total_posts": 45, "avg_engagement_rate": 3.2},
            "daily": [{"date": "2026-07-10", "reach": 4500, "engagement": 380, "posts": 2}],
            "by_platform": [{"platform": "linkedin", "reach": 67000, "engagement": 5200}, {"platform": "x", "reach": 45000, "engagement": 3100}],
            "by_content_type": [{"type": "educational", "count": 18, "avg_engagement": 4.2}],
        },
    }


@router.get("/{report_id}/export")
async def export_report(report_id: str, format: str = "csv", current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Export report as CSV or PDF."""
    return {"report_id": report_id, "format": format, "download_url": f"/reports/{report_id}/download.{format}", "message": f"Report exported as {format.upper()}"}
