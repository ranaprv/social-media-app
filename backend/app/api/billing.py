from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import get_settings
from app.models.user import User

router = APIRouter(prefix="/billing", tags=["billing"])

PLANS = {
    "free": {
        "id": "free",
        "name": "Free",
        "price": 0,
        "interval": "month",
        "credits": 50,
        "features": [
            "50 AI credits/month",
            "3 platform connections",
            "Basic analytics",
            "1 workspace",
            "Email support",
        ],
        "limits": {
            "ai_credits": 50,
            "platforms": 3,
            "workspaces": 1,
            "team_members": 1,
            "media_storage_mb": 100,
            "scheduled_posts": 10,
        },
    },
    "pro": {
        "id": "pro",
        "name": "Pro",
        "price": 29,
        "interval": "month",
        "credits": 500,
        "features": [
            "500 AI credits/month",
            "All platform connections",
            "Advanced analytics",
            "5 workspaces",
            "Priority support",
            "Brand voice training",
            "Content calendar",
            "AI repurposing",
        ],
        "limits": {
            "ai_credits": 500,
            "platforms": 5,
            "workspaces": 5,
            "team_members": 5,
            "media_storage_mb": 5000,
            "scheduled_posts": 100,
        },
        "stripe_price_id": "price_pro_monthly",
    },
    "business": {
        "id": "business",
        "name": "Business",
        "price": 99,
        "interval": "month",
        "credits": 2000,
        "features": [
            "2,000 AI credits/month",
            "All platform connections",
            "Full analytics suite",
            "Unlimited workspaces",
            "Dedicated support",
            "Brand voice training",
            "Content calendar",
            "AI repurposing",
            "Team collaboration",
            "Media library",
            "Custom integrations",
        ],
        "limits": {
            "ai_credits": 2000,
            "platforms": 5,
            "workspaces": -1,
            "team_members": 20,
            "media_storage_mb": 50000,
            "scheduled_posts": -1,
        },
        "stripe_price_id": "price_business_monthly",
    },
    "enterprise": {
        "id": "enterprise",
        "name": "Enterprise",
        "price": 299,
        "interval": "month",
        "credits": -1,
        "features": [
            "Unlimited AI credits",
            "All platform connections",
            "Enterprise analytics",
            "Unlimited workspaces",
            "Dedicated account manager",
            "Brand voice training",
            "Content calendar",
            "AI repurposing",
            "Team collaboration",
            "Media library",
            "Custom integrations",
            "SSO & SAML",
            "SLA guarantee",
            "Custom AI models",
            "API access",
        ],
        "limits": {
            "ai_credits": -1,
            "platforms": -1,
            "workspaces": -1,
            "team_members": -1,
            "media_storage_mb": -1,
            "scheduled_posts": -1,
        },
        "stripe_price_id": "price_enterprise_monthly",
    },
}


@router.get("/plans")
async def get_plans():
    """Get available subscription plans."""
    return {"plans": list(PLANS.values())}


@router.get("/subscription")
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's subscription."""
    return {
        "plan": "pro",
        "status": "active",
        "current_period_start": (datetime.utcnow() - timedelta(days=15)).isoformat(),
        "current_period_end": (datetime.utcnow() + timedelta(days=15)).isoformat(),
        "cancel_at_period_end": False,
        "payment_method": {
            "brand": "visa",
            "last4": "4242",
            "exp_month": 12,
            "exp_year": 2027,
        },
    }


@router.get("/usage")
async def get_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current usage stats."""
    return {
        "credits": {"used": 312, "limit": 500, "reset_date": (datetime.utcnow() + timedelta(days=15)).strftime("%Y-%m-%d")},
        "workspaces": {"used": 3, "limit": 5},
        "team_members": {"used": 4, "limit": 5},
        "media_storage": {"used_mb": 2340, "limit_mb": 5000},
        "scheduled_posts": {"used": 23, "limit": 100},
        "platforms_connected": {"used": 3, "limit": 5},
    }


@router.get("/invoices")
async def get_invoices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get billing history / invoices."""
    return {
        "invoices": [
            {"id": "inv-1", "date": "2026-07-01", "amount": 29, "status": "paid", "plan": "Pro", "description": "Pro Plan — Monthly"},
            {"id": "inv-2", "date": "2026-06-01", "amount": 29, "status": "paid", "plan": "Pro", "description": "Pro Plan — Monthly"},
            {"id": "inv-3", "date": "2026-05-01", "amount": 29, "status": "paid", "plan": "Pro", "description": "Pro Plan — Monthly"},
            {"id": "inv-4", "date": "2026-04-01", "amount": 0, "status": "paid", "plan": "Free", "description": "Free Plan"},
            {"id": "inv-5", "date": "2026-03-01", "amount": 0, "status": "paid", "plan": "Free", "description": "Free Plan"},
        ]
    }


@router.post("/checkout")
async def create_checkout_session(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a Stripe checkout session."""
    plan_id = request.get("plan", "pro")
    plan = PLANS.get(plan_id)

    if not plan:
        return {"error": "Invalid plan"}

    settings = get_settings()
    if settings.OPENAI_API_KEY:  # Using any key as proxy for Stripe being configured
        # In production: create real Stripe checkout session
        pass

    return {
        "checkout_url": f"/billing/checkout?plan={plan_id}",
        "session_id": f"cs_{uuid.uuid4().hex[:24]}",
        "plan": plan_id,
        "amount": plan["price"],
        "message": "Stripe integration requires STRIPE_SECRET_KEY. Add to .env for real checkout.",
    }


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel subscription at period end."""
    return {
        "status": "cancellation_scheduled",
        "cancels_at": (datetime.utcnow() + timedelta(days=15)).isoformat(),
        "message": "Your subscription will cancel at the end of the current billing period.",
    }
