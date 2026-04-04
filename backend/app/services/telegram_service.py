"""
Telegram Bot messaging service.
Used as the free WhatsApp alternative for the hackathon demo.

Send flow:
  - Bot sends a message to a chat_id (user's Telegram chat)
  - Users must first /start the bot to get a chat_id
  - For NGO dashboard testing, TELEGRAM_TEST_CHAT_ID in .env is used

Telegram Bot API docs: https://core.telegram.org/bots/api
"""
import httpx
from typing import Optional

from app.core.config import settings
from app.config.logger import get_logger

logger = get_logger(__name__)

TELEGRAM_API = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"

# Sample reminder templates per language for the test endpoint
SAMPLE_MESSAGES = {
    "hi": "⚖️ *CourtAlert रिमाइंडर*\n\nआपकी अगली सुनवाई *3 दिन बाद* है।\n📅 तारीख: 10 मई 2026\n🏛️ कोर्ट: जिला न्यायालय, पुणे\n📋 केस: Patil vs State\n\nकृपया समय पर उपस्थित हों।",
    "mr": "⚖️ *CourtAlert आठवण*\n\nतुमची पुढील सुनावणी *3 दिवसांनंतर* आहे।\n📅 तारीख: 10 मे 2026\n🏛️ न्यायालय: जिल्हा न्यायालय, पुणे\n📋 केस: Patil vs State\n\nकृपया वेळेवर उपस्थित राहा।",
    "te": "⚖️ *CourtAlert రిమైండర్*\n\nమీ తదుపరి విచారణ *3 రోజుల తర్వాత* ఉంది.\n📅 తేదీ: 10 మే 2026\n🏛️ కోర్టు: జిల్లా కోర్టు, పూణే\n📋 కేసు: Patil vs State",
    "ta": "⚖️ *CourtAlert நினைவூட்டல்*\n\nஉங்கள் அடுத்த விசாரணை *3 நாட்களில்* உள்ளது.\n📅 தேதி: 10 மே 2026\n🏛️ நீதிமன்றம்: மாவட்ட நீதிமன்றம், புனே",
    "kn": "⚖️ *CourtAlert ಜ್ಞಾಪನೆ*\n\nನಿಮ್ಮ ಮುಂದಿನ ವಿಚಾರಣೆ *3 ದಿನಗಳಲ್ಲಿ* ಇದೆ.\n📅 ದಿನಾಂಕ: 10 ಮೇ 2026\n🏛️ ನ್ಯಾಯಾಲಯ: ಜಿಲ್ಲಾ ನ್ಯಾಯಾಲಯ, ಪುಣೆ",
    "en": "⚖️ *CourtAlert Reminder*\n\nYour next hearing is in *3 days*.\n📅 Date: 10 May 2026\n🏛️ Court: District Court, Pune\n📋 Case: Patil vs State\n\nPlease be present on time.",
}


async def send_message(chat_id: str, text: str) -> Optional[str]:
    """
    Send a Telegram message. Returns message_id on success, None on failure.
    """
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not configured — skipping send")
        return None

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{TELEGRAM_API}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "Markdown",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            msg_id = str(data["result"]["message_id"])
            logger.info(f"Telegram message sent to {chat_id}: message_id={msg_id}")
            return msg_id
    except Exception as e:
        logger.error(f"Telegram send failed: {e}")
        return None


async def send_test_reminder(language: str = "hi") -> Optional[str]:
    """
    Send a sample court reminder to the configured test chat ID.
    Used by POST /notifications/test.
    """
    chat_id = settings.TELEGRAM_TEST_CHAT_ID
    if not chat_id:
        logger.warning("TELEGRAM_TEST_CHAT_ID not set — cannot send test message")
        return None

    text = SAMPLE_MESSAGES.get(language, SAMPLE_MESSAGES["en"])
    return await send_message(chat_id, text)
