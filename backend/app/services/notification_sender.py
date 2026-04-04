"""
Notification sender — abstraction over Telegram (demo) and Twilio SMS (prod).

Priority:
  1. Twilio SMS  — if TWILIO_ACCOUNT_SID is configured
  2. Telegram    — fallback for hackathon demo (sends to TELEGRAM_TEST_CHAT_ID)
"""
from typing import Optional

import httpx

from app.core.config import settings
from app.config.logger import get_logger

logger = get_logger(__name__)


async def send_alert(
    *,
    phone_number: str,
    message: str,
) -> tuple[bool, Optional[str], Optional[str]]:
    """
    Send an alert message.

    Returns:
        (success: bool, sid: Optional[str], error: Optional[str])
    """
    if settings.TWILIO_ACCOUNT_SID:
        return await _send_twilio_sms(phone_number=phone_number, message=message)
    else:
        return await _send_telegram(message=message)


# ---------------------------------------------------------------------------
# Twilio SMS
# ---------------------------------------------------------------------------

async def _send_twilio_sms(*, phone_number: str, message: str) -> tuple[bool, Optional[str], Optional[str]]:
    url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
    # Strip markdown for SMS (Twilio SMS doesn't render markdown)
    plain = message.replace("*", "").replace("_", "").replace("`", "")

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                url,
                data={
                    "From": settings.TWILIO_PHONE_NUMBER,
                    "To": phone_number,
                    "Body": plain,
                },
                auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
            )
            data = resp.json()
            if resp.status_code in (200, 201):
                sid = data.get("sid")
                logger.info(f"Twilio SMS sent to {phone_number}: {sid}")
                return True, sid, None
            else:
                error = data.get("message", str(resp.status_code))
                logger.error(f"Twilio SMS failed to {phone_number}: {error}")
                return False, None, error
    except Exception as exc:
        logger.error(f"Twilio SMS exception for {phone_number}: {exc}")
        return False, None, str(exc)


# ---------------------------------------------------------------------------
# Telegram (demo fallback)
# ---------------------------------------------------------------------------

async def _send_telegram(*, message: str) -> tuple[bool, Optional[str], Optional[str]]:
    chat_id = settings.TELEGRAM_TEST_CHAT_ID
    if not chat_id or not settings.TELEGRAM_BOT_TOKEN:
        return False, None, "Telegram not configured"

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"},
            )
            data = resp.json()
            if resp.status_code == 200 and data.get("ok"):
                msg_id = str(data["result"]["message_id"])
                logger.info(f"Telegram message sent: message_id={msg_id}")
                return True, msg_id, None
            else:
                error = data.get("description", "unknown error")
                logger.error(f"Telegram send failed: {error}")
                return False, None, error
    except Exception as exc:
        logger.error(f"Telegram exception: {exc}")
        return False, None, str(exc)
