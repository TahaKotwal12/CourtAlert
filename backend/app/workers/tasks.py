"""
Celery tasks for CourtAlert.

Task 1 — daily_sync_task  (7:00 AM IST)
    Re-fetches hearing data from eCourts for all active registrations.

Task 2 — daily_alert_task  (8:00 AM IST)
    Checks which hearings are in 1 / 3 / 7 days and sends alerts.
    Respects the unique constraint: one notification per (registration, hearing, days_before).
"""
import asyncio
from datetime import date, timedelta

from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.workers.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.registration import Registration
from app.models.hearing import Hearing
from app.models.notification import Notification
from app.models.enums import ChannelType, NotificationStatus
from app.services import ecourts
from app.services.message_generator import build_message
from app.services.notification_sender import send_alert
from app.config.logger import get_logger

logger = get_logger(__name__)

ALERT_DAYS = [7, 3, 1]  # send alerts this many days before hearing


# =============================================================================
# Task 1 — Sync hearings from eCourts
# =============================================================================

@celery_app.task(name="app.workers.tasks.daily_sync_task", bind=True, max_retries=2)
def daily_sync_task(self):
    """Re-sync hearing data for all active registrations."""
    try:
        result = asyncio.run(_async_sync_all())
        logger.info(f"[SYNC] Done: {result}")
        return result
    except Exception as exc:
        logger.error(f"[SYNC] Failed: {exc}")
        raise self.retry(exc=exc, countdown=300)  # retry in 5 min


async def _async_sync_all() -> dict:
    synced = 0
    failed = 0

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Registration).where(Registration.is_active == True)
        )
        registrations = result.scalars().all()

        for reg in registrations:
            try:
                case_data = await ecourts.fetch_case(reg.cnr_number)
                if not case_data:
                    logger.warning(f"[SYNC] No data for CNR {reg.cnr_number}")
                    failed += 1
                    continue

                # Update case metadata
                reg.case_title    = case_data["case_title"]
                reg.court_name    = case_data["court_name"]
                reg.state_code    = case_data["state_code"]
                reg.district_code = case_data["district_code"]

                # Get existing hearing dates
                h_result = await db.execute(
                    select(Hearing.hearing_date).where(Hearing.registration_id == reg.id)
                )
                existing_dates = {row[0] for row in h_result.fetchall()}

                # Add new hearings
                for h in case_data["hearings"]:
                    if h["hearing_date"] not in existing_dates:
                        db.add(Hearing(
                            registration_id=reg.id,
                            hearing_date=h["hearing_date"],
                            hearing_type=h.get("hearing_type"),
                            court_room=h.get("court_room"),
                            judge_name=h.get("judge_name"),
                            purpose=h.get("purpose"),
                            is_completed=h.get("is_completed", False),
                        ))

                synced += 1

            except Exception as exc:
                logger.error(f"[SYNC] Error for {reg.cnr_number}: {exc}")
                failed += 1

        await db.commit()

    return {"synced": synced, "failed": failed}


# =============================================================================
# Task 2 — Send hearing alerts
# =============================================================================

@celery_app.task(name="app.workers.tasks.daily_alert_task", bind=True, max_retries=2)
def daily_alert_task(self):
    """Check upcoming hearings and send alerts for 7/3/1 day thresholds."""
    try:
        result = asyncio.run(_async_send_alerts())
        logger.info(f"[ALERTS] Done: {result}")
        return result
    except Exception as exc:
        logger.error(f"[ALERTS] Failed: {exc}")
        raise self.retry(exc=exc, countdown=300)


async def _async_send_alerts() -> dict:
    today = date.today()
    sent = 0
    skipped = 0
    failed = 0

    async with AsyncSessionLocal() as db:
        # Load all active registrations with their upcoming hearings
        result = await db.execute(
            select(Registration)
            .where(Registration.is_active == True)
            .options(selectinload(Registration.hearings))
        )
        registrations = result.scalars().all()

        for reg in registrations:
            upcoming = [
                h for h in reg.hearings
                if not h.is_completed and h.hearing_date >= today
            ]

            for hearing in upcoming:
                days_until = (hearing.hearing_date - today).days

                if days_until not in ALERT_DAYS:
                    continue

                # Check: already sent this alert? (unique constraint guard)
                dup = await db.execute(
                    select(Notification).where(
                        and_(
                            Notification.registration_id == reg.id,
                            Notification.hearing_id == hearing.id,
                            Notification.days_before == days_until,
                        )
                    )
                )
                if dup.scalar_one_or_none():
                    skipped += 1
                    continue

                # Build message (LLM via Featherless.ai, fallback to template)
                message = await build_message(
                    case_title=reg.case_title or reg.cnr_number,
                    hearing_date=hearing.hearing_date,
                    court_name=reg.court_name or "Court",
                    court_room=hearing.court_room or "—",
                    language=reg.language,
                    days_before=days_until,
                )

                # Send alert
                success, sid, error = await send_alert(
                    phone_number=reg.phone_number,
                    message=message,
                )

                # Determine channel used
                from app.core.config import settings as cfg
                channel = ChannelType.sms if cfg.TWILIO_ACCOUNT_SID else ChannelType.whatsapp

                # Log to notifications table
                notification = Notification(
                    registration_id=reg.id,
                    hearing_id=hearing.id,
                    channel=channel,
                    status=NotificationStatus.delivered if success else NotificationStatus.failed,
                    message_text=message,
                    message_language=reg.language,
                    days_before=days_until,
                    twilio_sid=sid,
                    error_message=error,
                )
                db.add(notification)

                if success:
                    sent += 1
                    logger.info(
                        f"[ALERT] Sent {days_until}d reminder → {reg.phone_number} "
                        f"({reg.cnr_number}, hearing {hearing.hearing_date})"
                    )
                else:
                    failed += 1
                    logger.error(
                        f"[ALERT] Failed {days_until}d reminder → {reg.phone_number} "
                        f"({reg.cnr_number}): {error}"
                    )

        await db.commit()

    return {"sent": sent, "skipped": skipped, "failed": failed}


# =============================================================================
# Manual trigger helpers (for testing via API or shell)
# =============================================================================

@celery_app.task(name="app.workers.tasks.trigger_alert_for_registration")
def trigger_alert_for_registration(registration_id: str):
    """Manually trigger alerts for a single registration (test/debug use)."""
    asyncio.run(_async_alert_single(registration_id))


async def _async_alert_single(registration_id: str) -> None:
    import uuid
    today = date.today()

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Registration)
            .where(Registration.id == uuid.UUID(registration_id))
            .options(selectinload(Registration.hearings))
        )
        reg = result.scalar_one_or_none()
        if not reg:
            logger.warning(f"[ALERT] Registration {registration_id} not found")
            return

        for hearing in reg.hearings:
            if hearing.is_completed or hearing.hearing_date < today:
                continue
            days_until = (hearing.hearing_date - today).days
            logger.info(f"[ALERT] {reg.cnr_number} — next hearing in {days_until} days")

        await db.commit()
