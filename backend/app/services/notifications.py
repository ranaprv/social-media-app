"""Webhook notification service — notify on publish success/failure.

Supports:
  - Slack webhooks (incoming webhook URL)
  - Email notifications (via the existing email service)
  - Generic webhook (POST to any URL)

Notifications are triggered by the publish_post task after each attempt.
"""
import httpx
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


# Notification types
NOTIFICATION_TYPES = {
    "publish_success": {
        "template": "✅ Published to {platform}: {post_title}",
        "color": "#22c55e",
    },
    "publish_failed": {
        "template": "❌ Failed to publish to {platform}: {post_title}\nError: {error}",
        "color": "#ef4444",
    },
    "token_expiring": {
        "template": "⚠️ {platform} token expiring soon for {workspace}",
        "color": "#f59e0b",
    },
    "queue_empty": {
        "template": "📭 Publishing queue is empty",
        "color": "#64748b",
    },
    "series_created": {
        "template": "📅 Recurring series '{series}' created: {count} posts scheduled",
        "color": "#3b82f6",
    },
}


async def send_notification(
    notification_type: str,
    workspace_id: str,
    data: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Send a notification through configured channels.

    Args:
        notification_type: Key from NOTIFICATION_TYPES.
        workspace_id: The workspace to notify for.
        data: Template data (post_title, platform, error, etc.).
        config: Override config. If None, loads from workspace settings.

    Returns:
        {sent: int, failed: int, channels: [...]}
    """
    if notification_type not in NOTIFICATION_TYPES:
        return {"error": f"Unknown notification type: {notification_type}"}

    if config is None:
        config = await _load_workspace_notification_config(workspace_id)

    channels = config.get("channels", [])
    results = {"sent": 0, "failed": 0, "channels": []}

    template_info = NOTIFICATION_TYPES[notification_type]
    message = template_info["template"].format(**data)

    for channel in channels:
        channel_type = channel.get("type", "")
        try:
            if channel_type == "slack":
                await _send_slack(channel, message, template_info["color"], data)
                results["sent"] += 1
                results["channels"].append({"type": "slack", "status": "sent"})
            elif channel_type == "email":
                await _send_email(channel, notification_type, message, data)
                results["sent"] += 1
                results["channels"].append({"type": "email", "status": "sent"})
            elif channel_type == "webhook":
                await _send_webhook(channel, notification_type, message, data)
                results["sent"] += 1
                results["channels"].append({"type": "webhook", "status": "sent"})
            else:
                logger.warning(f"Unknown notification channel type: {channel_type}")
        except Exception as e:
            results["failed"] += 1
            results["channels"].append({
                "type": channel_type,
                "status": "failed",
                "error": str(e),
            })
            logger.error(f"Notification failed ({channel_type}): {e}")

    return results


async def _send_slack(
    channel: dict[str, Any],
    message: str,
    color: str,
    data: dict[str, Any],
) -> None:
    """Send notification to Slack via incoming webhook."""
    webhook_url = channel.get("webhook_url", "")
    if not webhook_url:
        raise ValueError("Slack webhook_url not configured")

    payload = {
        "attachments": [
            {
                "color": color,
                "text": message,
                "fields": [
                    {"title": k, "value": str(v), "short": True}
                    for k, v in data.items()
                    if k in ("platform", "post_title", "scheduled_at", "error")
                ],
                "footer": "Social Media Manager",
                "ts": int(datetime.utcnow().timestamp()),
            }
        ]
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(webhook_url, json=payload)
        if response.status_code != 200:
            raise ValueError(f"Slack webhook returned {response.status_code}")


async def _send_email(
    channel: dict[str, Any],
    notification_type: str,
    message: str,
    data: dict[str, Any],
) -> None:
    """Send notification via email."""
    from app.core.config import get_settings
    settings = get_settings()

    to_email = channel.get("email", "")
    if not to_email:
        raise ValueError("Email address not configured")

    # Use the existing email service
    from app.services.email import send_email
    subject = f"[SMM] {NOTIFICATION_TYPES[notification_type]['template'].split(chr(10))[0].format(**data)}"
    await send_email(
        to_email=to_email,
        subject=subject,
        body=message,
    )


async def _send_webhook(
    channel: dict[str, Any],
    notification_type: str,
    message: str,
    data: dict[str, Any],
) -> None:
    """Send notification to a generic webhook URL."""
    webhook_url = channel.get("webhook_url", "")
    if not webhook_url:
        raise ValueError("Webhook URL not configured")

    payload = {
        "type": notification_type,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat(),
        "source": "social-media-manager",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        headers = {}
        if channel.get("secret"):
            import hmac
            import hashlib
            body = json.dumps(payload)
            signature = hmac.new(
                channel["secret"].encode(), body.encode(), hashlib.sha256
            ).hexdigest()
            headers["X-Signature-256"] = f"sha256={signature}"

        response = await client.post(webhook_url, json=payload, headers=headers)
        if response.status_code >= 400:
            raise ValueError(f"Webhook returned {response.status_code}")


async def _load_workspace_notification_config(
    workspace_id: str,
) -> dict[str, Any]:
    """Load notification config for a workspace.

    Returns default config if none is set.
    """
    # Default: no notifications configured
    return {
        "channels": [],
        "enabled": False,
    }


def configure_slack_notification(webhook_url: str) -> dict[str, Any]:
    """Create a Slack notification channel config."""
    return {"type": "slack", "webhook_url": webhook_url}


def configure_email_notification(email: str) -> dict[str, Any]:
    """Create an email notification channel config."""
    return {"type": "email", "email": email}


def configure_webhook_notification(webhook_url: str, secret: str | None = None) -> dict[str, Any]:
    """Create a generic webhook notification channel config."""
    config: dict[str, Any] = {"type": "webhook", "webhook_url": webhook_url}
    if secret:
        config["secret"] = secret
    return config
