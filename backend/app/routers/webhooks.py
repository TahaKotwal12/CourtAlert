"""
Webhook endpoints called by Twilio.

POST /webhook/twilio        — inbound WhatsApp/SMS messages
POST /webhook/twilio/status — delivery status callbacks

Twilio sends multipart/form-data (not JSON).
Responses for the inbound endpoint must be TwiML XML.
"""
import re
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.logger import get_logger
from app.core.database import get_db
from app.models.enums import CommandType, NotificationStatus
from app.models.notification import Notification
from app.models.registration import Registration
from app.models.whatsapp_command import WhatsappCommand

logger = get_logger(__name__)

router = APIRouter(prefix="/webhook", tags=["Webhooks"])

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TWIML_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Message>{message}</Message>
</Response>"""

CNR_PATTERN = re.compile(r"[A-Z]{4}\d{11}", re.IGNORECASE)
LANG_PATTERN = re.compile(r"\b(hi|mr|te|ta|kn|en)\b", re.IGNORECASE)


def _twiml(message: str) -> Response:
    return Response(content=TWIML_RESPONSE.format(message=message), media_type="application/xml")


def _parse_command(body: str) -> tuple[CommandType, str | None, str | None]:
    """
    Parse inbound message body into (command_type, cnr, language).

    Supported formats:
      REG MHPN0101234562024 HI  → register
      STOP                       → deactivate all
      STATUS                     → get current status
      <anything else>            → UNKNOWN
    """
    body = body.strip().upper()
    parts = body.split()

    if not parts:
        return CommandType.UNKNOWN, None, None

    cmd = parts[0]

    if cmd == "REG":
        cnr_match  = CNR_PATTERN.search(body)
        lang_match = LANG_PATTERN.search(body)
        cnr  = cnr_match.group(0).upper()  if cnr_match  else None
        lang = lang_match.group(0).lower() if lang_match else "hi"
        return CommandType.REG, cnr, lang

    if cmd == "STOP":
        return CommandType.STOP, None, None

    if cmd == "STATUS":
        return CommandType.STATUS, None, None

    return CommandType.UNKNOWN, None, None


# ---------------------------------------------------------------------------
# POST /webhook/twilio  — inbound messages
# ---------------------------------------------------------------------------

@router.post("/twilio")
async def twilio_inbound(
    From:       Annotated[str, Form()],
    Body:       Annotated[str, Form()],
    MessageSid: Annotated[str, Form()] = "",
    db:         AsyncSession = Depends(get_db),
):
    # Normalize sender number (Twilio prefixes whatsapp:+91...)
    from_number = From.replace("whatsapp:", "").strip()

    logger.info(f"Inbound from {from_number}: {Body!r}")

    command_type, cnr, language = _parse_command(Body)

    # Save raw inbound command
    cmd_record = WhatsappCommand(
        from_number=from_number,
        body=Body,
        command_type=command_type,
        cnr_extracted=cnr,
        language_extracted=language,
        twilio_sid=MessageSid or None,
    )

    # -----------------------------------------------------------------------
    # REG command
    # -----------------------------------------------------------------------
    if command_type == CommandType.REG:
        if not cnr:
            reply = (
                "❌ Invalid format. Please send:\n"
                "REG <CNR_NUMBER> <LANGUAGE>\n\n"
                "Example: REG MHPN0101234562024 HI\n"
                "Languages: HI MR TE TA KN EN"
            )
            cmd_record.response_sent = reply
            db.add(cmd_record)
            return _twiml(reply)

        # Check for existing active registration
        result = await db.execute(
            select(Registration).where(
                Registration.cnr_number == cnr,
                Registration.phone_number == from_number,
                Registration.is_active == True,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            reply = (
                f"✅ You are already registered for case:\n"
                f"{existing.case_title or cnr}\n\n"
                f"You will receive reminders 7, 3 and 1 day before each hearing."
            )
            cmd_record.registration_id = existing.id
            cmd_record.response_sent = reply
            db.add(cmd_record)
            return _twiml(reply)

        # Create new registration (self-registered — registered_by is NULL)
        from app.services import ecourts as ecourts_service
        case_data = await ecourts_service.fetch_case(cnr)

        if not case_data:
            reply = (
                f"❌ CNR number {cnr} not found in eCourts records.\n"
                "Please check the number and try again."
            )
            cmd_record.response_sent = reply
            db.add(cmd_record)
            return _twiml(reply)

        reg = Registration(
            cnr_number=cnr,
            phone_number=from_number,
            language=language or "hi",
            case_title=case_data["case_title"],
            court_name=case_data["court_name"],
            state_code=case_data["state_code"],
            district_code=case_data["district_code"],
            registered_by=None,  # self-registered
        )
        db.add(reg)
        await db.flush()

        from app.models.hearing import Hearing
        for h in case_data["hearings"]:
            db.add(Hearing(
                registration_id=reg.id,
                hearing_date=h["hearing_date"],
                hearing_type=h.get("hearing_type"),
                court_room=h.get("court_room"),
                judge_name=h.get("judge_name"),
                purpose=h.get("purpose"),
                is_completed=h.get("is_completed", False),
            ))

        next_h = next(
            (h["hearing_date"] for h in case_data["hearings"] if not h.get("is_completed")),
            None,
        )

        reply = (
            f"✅ Registered successfully!\n\n"
            f"📋 Case: {case_data['case_title']}\n"
            f"🏛️ Court: {case_data['court_name']}\n"
            f"📅 Next hearing: {next_h.strftime('%d %b %Y') if next_h else 'Not scheduled'}\n\n"
            f"You will receive reminders 7, 3 and 1 day before each hearing.\n"
            f"Send STOP to unsubscribe."
        )
        cmd_record.registration_id = reg.id
        cmd_record.response_sent = reply
        db.add(cmd_record)
        return _twiml(reply)

    # -----------------------------------------------------------------------
    # STOP command
    # -----------------------------------------------------------------------
    if command_type == CommandType.STOP:
        result = await db.execute(
            select(Registration).where(
                Registration.phone_number == from_number,
                Registration.is_active == True,
            )
        )
        registrations = result.scalars().all()

        for reg in registrations:
            reg.is_active = False

        count = len(registrations)
        reply = (
            f"✅ Unsubscribed. {count} case(s) deactivated.\n"
            "You will no longer receive alerts.\n\n"
            "To re-register, send: REG <CNR_NUMBER> <LANGUAGE>"
        ) if count else (
            "ℹ️ You have no active registrations."
        )
        cmd_record.response_sent = reply
        db.add(cmd_record)
        return _twiml(reply)

    # -----------------------------------------------------------------------
    # STATUS command
    # -----------------------------------------------------------------------
    if command_type == CommandType.STATUS:
        result = await db.execute(
            select(Registration).where(
                Registration.phone_number == from_number,
                Registration.is_active == True,
            )
        )
        registrations = result.scalars().all()

        if not registrations:
            reply = (
                "ℹ️ You have no active case registrations.\n\n"
                "To register, send: REG <CNR_NUMBER> <LANGUAGE>"
            )
        else:
            lines = [f"📋 You have {len(registrations)} active case(s):\n"]
            for reg in registrations:
                lines.append(f"• {reg.case_title or reg.cnr_number}")
            reply = "\n".join(lines)

        cmd_record.response_sent = reply
        db.add(cmd_record)
        return _twiml(reply)

    # -----------------------------------------------------------------------
    # UNKNOWN command
    # -----------------------------------------------------------------------
    reply = (
        "👋 Welcome to CourtAlert!\n\n"
        "Commands:\n"
        "• REG <CNR> <LANG> — Register a case\n"
        "• STATUS — View your active cases\n"
        "• STOP — Unsubscribe from all alerts\n\n"
        "Example: REG MHPN0101234562024 HI\n"
        "Languages: HI MR TE TA KN EN"
    )
    cmd_record.response_sent = reply
    db.add(cmd_record)
    return _twiml(reply)


# ---------------------------------------------------------------------------
# POST /webhook/twilio/status  — delivery status callback
# ---------------------------------------------------------------------------

@router.post("/twilio/status")
async def twilio_status(
    MessageSid:    Annotated[str, Form()],
    MessageStatus: Annotated[str, Form()],
    db:            AsyncSession = Depends(get_db),
):
    logger.info(f"Twilio status callback: sid={MessageSid} status={MessageStatus}")

    result = await db.execute(
        select(Notification).where(Notification.twilio_sid == MessageSid)
    )
    notification = result.scalar_one_or_none()

    if notification:
        if MessageStatus == "delivered":
            notification.status = NotificationStatus.delivered
            from datetime import datetime, timezone
            notification.delivered_at = datetime.now(timezone.utc)
        elif MessageStatus in ("failed", "undelivered"):
            notification.status = NotificationStatus.failed
            notification.error_message = f"Twilio status: {MessageStatus}"
        elif MessageStatus == "sent":
            notification.status = NotificationStatus.sent

    return {"received": True}
