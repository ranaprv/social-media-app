"""Stripe webhook handler."""
from fastapi import APIRouter, Request, HTTPException
import stripe
import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events."""
    settings = get_settings()
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not settings.STRIPE_WEBHOOK_SECRET:
        logger.warning("Stripe webhook secret not configured")
        return {"status": "skipped", "reason": "webhook secret not configured"}

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail="Webhook error")

    # Handle event types
    event_type = event["type"]

    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        logger.info(f"Checkout completed: {session.get('id')}")
        # TODO: Update subscription in database

    elif event_type == "customer.subscription.updated":
        subscription = event["data"]["object"]
        logger.info(f"Subscription updated: {subscription.get('id')}")
        # TODO: Update subscription status

    elif event_type == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        logger.info(f"Subscription deleted: {subscription.get('id')}")
        # TODO: Mark subscription as cancelled

    elif event_type == "invoice.payment_failed":
        invoice = event["data"]["object"]
        logger.info(f"Payment failed: {invoice.get('id')}")
        # TODO: Notify user, mark subscription as past_due

    else:
        logger.info(f"Unhandled event type: {event_type}")

    return {"status": "ok"}
