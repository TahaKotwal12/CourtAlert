import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.enums import NotificationStatus, UserRole
from app.models.notification import Notification
from app.models.registration import Registration
from app.models.user import User
from app.schemas.notifications import (
    NotificationListItem,
    NotificationsListResponse,
    TestNotificationRequest,
    TestNotificationResponse,
)
from app.services import telegram_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


# ---------------------------------------------------------------------------
# GET /notifications
# ---------------------------------------------------------------------------

@router.get("", response_model=NotificationsListResponse)
async def list_notifications(
    status_filter: Optional[str]  = Query(default=None, alias="status"),
    from_date:     Optional[date] = Query(default=None),
    to_date:       Optional[date] = Query(default=None),
    db:            AsyncSession   = Depends(get_db),
    current_user:  User           = Depends(get_current_user),
):
    query = select(Notification)

    # Scope: NGO users only see notifications for their own registrations
    if current_user.role != UserRole.admin:
        query = (
            query.join(Registration, Notification.registration_id == Registration.id)
            .where(Registration.registered_by == current_user.id)
        )

    if status_filter:
        try:
            s = NotificationStatus(status_filter)
            query = query.where(Notification.status == s)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {[s.value for s in NotificationStatus]}",
            )

    if from_date:
        query = query.where(func.date(Notification.sent_at) >= from_date)
    if to_date:
        query = query.where(func.date(Notification.sent_at) <= to_date)

    # Count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()

    result = await db.execute(query.order_by(Notification.sent_at.desc()))
    items = result.scalars().all()

    return NotificationsListResponse(items=list(items), total=total)


# ---------------------------------------------------------------------------
# GET /notifications/{case_id}
# ---------------------------------------------------------------------------

@router.get("/{case_id}", response_model=list[NotificationListItem])
async def get_case_notifications(
    case_id:      uuid.UUID,
    db:           AsyncSession = Depends(get_db),
    current_user: User         = Depends(get_current_user),
):
    # Verify case exists and user has access
    reg_result = await db.execute(select(Registration).where(Registration.id == case_id))
    reg = reg_result.scalar_one_or_none()

    if not reg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    if current_user.role != UserRole.admin and reg.registered_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    result = await db.execute(
        select(Notification)
        .where(Notification.registration_id == case_id)
        .order_by(Notification.sent_at.desc())
    )
    return result.scalars().all()


# ---------------------------------------------------------------------------
# POST /notifications/test
# ---------------------------------------------------------------------------

@router.post("/test", response_model=TestNotificationResponse)
async def send_test_notification(
    payload:      TestNotificationRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Sends a sample court reminder via Telegram to verify messaging integration.
    Uses TELEGRAM_TEST_CHAT_ID from .env.
    """
    message_id = await telegram_service.send_test_reminder(language=payload.language)

    if message_id is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Telegram send failed. Check TELEGRAM_BOT_TOKEN and TELEGRAM_TEST_CHAT_ID in .env",
        )

    return TestNotificationResponse(
        status="sent",
        channel="telegram",
        message_id=message_id,
    )
