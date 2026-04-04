"""
Alert message generator for CourtAlert.

Primary:  Featherless.ai (DeepSeek-V3.2) — generates natural, empathetic messages
          in the litigant's language via OpenAI-compatible API.

Fallback: Hardcoded templates — used if LLM call fails or API key is missing.
          Tasks always get a message — no silent drops.
"""
import httpx
from datetime import date
from typing import Optional

from app.core.config import settings
from app.config.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Language metadata
# ---------------------------------------------------------------------------

LANGUAGE_NAMES = {
    "hi": "Hindi",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "en": "English",
}

# ---------------------------------------------------------------------------
# Fallback templates (used when LLM is unavailable)
# ---------------------------------------------------------------------------

_TEMPLATES: dict[str, str] = {
    "hi": (
        "⚖️ *CourtAlert रिमाइंडर*\n\n"
        "आपके केस *{case_title}* की सुनवाई *{days_label}* है।\n"
        "📅 तारीख: {hearing_date}\n"
        "🏛️ कोर्ट: {court_name}\n"
        "🚪 कक्ष: {court_room}\n\n"
        "कृपया समय पर उपस्थित हों।"
    ),
    "mr": (
        "⚖️ *CourtAlert आठवण*\n\n"
        "तुमच्या केस *{case_title}* ची सुनावणी *{days_label}* आहे।\n"
        "📅 तारीख: {hearing_date}\n"
        "🏛️ न्यायालय: {court_name}\n"
        "🚪 कक्ष: {court_room}\n\n"
        "कृपया वेळेवर उपस्थित राहा।"
    ),
    "ta": (
        "⚖️ *CourtAlert நினைவூட்டல்*\n\n"
        "உங்கள் வழக்கு *{case_title}* விசாரணை *{days_label}* உள்ளது.\n"
        "📅 தேதி: {hearing_date}\n"
        "🏛️ நீதிமன்றம்: {court_name}\n"
        "🚪 அறை: {court_room}\n\n"
        "தயவுசெய்து சரியான நேரத்தில் வாருங்கள்."
    ),
    "te": (
        "⚖️ *CourtAlert రిమైండర్*\n\n"
        "మీ కేసు *{case_title}* విచారణ *{days_label}* ఉంది.\n"
        "📅 తేదీ: {hearing_date}\n"
        "🏛️ కోర్టు: {court_name}\n"
        "🚪 గది: {court_room}\n\n"
        "దయచేసి సమయానికి హాజరవ్వండి."
    ),
    "kn": (
        "⚖️ *CourtAlert ಜ್ಞಾಪನೆ*\n\n"
        "ನಿಮ್ಮ ಕೇಸ್ *{case_title}* ವಿಚಾರಣೆ *{days_label}* ಇದೆ.\n"
        "📅 ದಿನಾಂಕ: {hearing_date}\n"
        "🏛️ ನ್ಯಾಯಾಲಯ: {court_name}\n"
        "🚪 ಕೊಠಡಿ: {court_room}\n\n"
        "ದಯವಿಟ್ಟು ಸಮಯಕ್ಕೆ ಹಾಜರಾಗಿ."
    ),
    "en": (
        "⚖️ *CourtAlert Reminder*\n\n"
        "Your case *{case_title}* has a hearing *{days_label}*.\n"
        "📅 Date: {hearing_date}\n"
        "🏛️ Court: {court_name}\n"
        "🚪 Room: {court_room}\n\n"
        "Please be present on time."
    ),
}

_DAY_LABELS: dict[str, dict[int, str]] = {
    "hi": {1: "कल", 3: "3 दिन बाद", 7: "7 दिन बाद"},
    "mr": {1: "उद्या", 3: "3 दिवसांनंतर", 7: "7 दिवसांनंतर"},
    "ta": {1: "நாளை", 3: "3 நாட்களில்", 7: "7 நாட்களில்"},
    "te": {1: "రేపు", 3: "3 రోజుల తర్వాత", 7: "7 రోజుల తర్వాత"},
    "kn": {1: "ನಾಳೆ", 3: "3 ದಿನಗಳಲ್ಲಿ", 7: "7 ದಿನಗಳಲ್ಲಿ"},
    "en": {1: "tomorrow", 3: "in 3 days", 7: "in 7 days"},
}


def _fallback_message(
    *,
    case_title: str,
    hearing_date: date,
    court_name: str,
    court_room: str,
    language: str,
    days_before: int,
) -> str:
    lang = language if language in _TEMPLATES else "en"
    label_map = _DAY_LABELS.get(lang, _DAY_LABELS["en"])
    days_label = label_map.get(days_before, f"in {days_before} days")
    date_str = hearing_date.strftime("%d %B %Y")

    return _TEMPLATES[lang].format(
        case_title=case_title or "Your Case",
        days_label=days_label,
        hearing_date=date_str,
        court_name=court_name or "Court",
        court_room=court_room or "—",
    )


# ---------------------------------------------------------------------------
# LLM prompt builder
# ---------------------------------------------------------------------------

def _build_prompt(
    *,
    case_title: str,
    hearing_date: date,
    court_name: str,
    court_room: str,
    language: str,
    days_before: int,
) -> str:
    lang_name = LANGUAGE_NAMES.get(language, "English")
    date_str = hearing_date.strftime("%d %B %Y")

    urgency = {1: "TOMORROW — extremely urgent", 3: "in 3 days — urgent", 7: "in 7 days"}.get(
        days_before, f"in {days_before} days"
    )

    return (
        f"You are CourtAlert, a legal notification service helping poor and unrepresented "
        f"litigants in India attend their court hearings.\n\n"
        f"Write a WhatsApp reminder message in {lang_name} with these details:\n"
        f"- Case: {case_title}\n"
        f"- Hearing date: {date_str} ({urgency})\n"
        f"- Court: {court_name}\n"
        f"- Court room: {court_room}\n\n"
        f"Requirements:\n"
        f"1. Write ONLY in {lang_name} (use native script)\n"
        f"2. Be warm, clear, and empathetic — this person may be anxious\n"
        f"3. Include: case name, exact date, court name, room number\n"
        f"4. End with a reminder to come on time\n"
        f"5. Keep it under 300 characters\n"
        f"6. Do NOT add any English translation or explanation\n"
        f"7. Start with the ⚖️ emoji and CourtAlert brand name in {lang_name}\n\n"
        f"Write only the message, nothing else."
    )


# ---------------------------------------------------------------------------
# Main async function
# ---------------------------------------------------------------------------

async def build_message(
    *,
    case_title: str,
    hearing_date: date,
    court_name: str,
    court_room: str,
    language: str,
    days_before: int,
) -> str:
    """
    Generate an alert message using Featherless.ai (DeepSeek-V3.2).
    Falls back to templates if LLM is unavailable or returns garbage.
    """
    if not settings.FEATHERLESS_API_KEY:
        logger.warning("[MSG] FEATHERLESS_API_KEY not set — using template fallback")
        return _fallback_message(
            case_title=case_title,
            hearing_date=hearing_date,
            court_name=court_name,
            court_room=court_room,
            language=language,
            days_before=days_before,
        )

    prompt = _build_prompt(
        case_title=case_title,
        hearing_date=hearing_date,
        court_name=court_name,
        court_room=court_room,
        language=language,
        days_before=days_before,
    )

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                f"{settings.FEATHERLESS_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.FEATHERLESS_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.FEATHERLESS_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300,
                    "temperature": 0.7,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            message = data["choices"][0]["message"]["content"].strip()

            if len(message) < 20:
                raise ValueError(f"LLM returned suspiciously short message: {message!r}")

            logger.info(f"[MSG] LLM generated {language} message ({len(message)} chars)")
            return message

    except Exception as exc:
        logger.error(f"[MSG] Featherless.ai failed, using template fallback: {exc}")
        return _fallback_message(
            case_title=case_title,
            hearing_date=hearing_date,
            court_name=court_name,
            court_room=court_room,
            language=language,
            days_before=days_before,
        )
