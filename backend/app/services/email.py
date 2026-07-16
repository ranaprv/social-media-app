"""Email service abstraction. Console in dev, SendGrid/SES in prod."""
import logging
from app.core.config import get_settings

logger = logging.getLogger(__name__)


async def send_email(to: str, subject: str, body: str, html: bool = False) -> bool:
    """Send an email. Returns True if sent successfully."""
    settings = get_settings()

    if settings.SENDGRID_API_KEY:
        return await _send_via_sendgrid(to, subject, body, html)

    # Dev fallback — log to console
    logger.info(f"[EMAIL] To: {to} | Subject: {subject}")
    logger.info(f"[EMAIL] Body: {body[:200]}")
    return True


async def _send_via_sendgrid(to: str, subject: str, body: str, html: bool) -> bool:
    """Send via SendGrid API."""
    try:
        import httpx
        settings = get_settings()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "personalizations": [{"to": [{"email": to}]}],
                    "from": {"email": settings.FROM_EMAIL},
                    "subject": subject,
                    "content": [{"type": "text/html" if html else "text/plain", "value": body}],
                },
            )
            return response.status_code in (200, 202)
    except Exception as e:
        logger.error(f"SendGrid error: {e}")
        return False
