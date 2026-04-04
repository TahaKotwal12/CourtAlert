from datetime import date, timedelta, datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.enums import ChannelType, NotificationStatus, UserRole
from app.models.hearing import Hearing
from app.models.notification import Notification
from app.models.registration import Registration
from app.models.user import User
from app.schemas.stats import (
    ChannelStats,
    DeliveryRateStats,
    OverviewStats,
    UpcomingHearing,
)

router = APIRouter(prefix="/stats", tags=["Stats"])


# ---------------------------------------------------------------------------
# Scoping helper
# ---------------------------------------------------------------------------

def _scope(query, current_user: User):
    """Restrict query to current user's registrations unless admin."""
    if current_user.role != UserRole.admin:
        query = query.where(Registration.registered_by == current_user.id)
    return query


# ---------------------------------------------------------------------------
# GET /stats/overview
# ---------------------------------------------------------------------------

@router.get("/overview", response_model=OverviewStats)
async def overview(
    db:           AsyncSession = Depends(get_db),
    current_user: User         = Depends(get_current_user),
):
    base_reg = select(Registration)
    base_reg = _scope(base_reg, current_user)

    # Total cases
    total_result = await db.execute(select(func.count()).select_from(base_reg.subquery()))
    total_cases = total_result.scalar_one()

    # Active cases
    active_result = await db.execute(
        select(func.count()).select_from(
            _scope(select(Registration).where(Registration.is_active == True), current_user).subquery()
        )
    )
    active_cases = active_result.scalar_one()

    # Alerts sent in last 30 days
    since_30d = datetime.now(timezone.utc) - timedelta(days=30)
    notif_query = select(Notification).join(
        Registration, Notification.registration_id == Registration.id
    )
    notif_query = _scope(notif_query, current_user)
    notif_query = notif_query.where(Notification.sent_at >= since_30d)

    alerts_result = await db.execute(select(func.count()).select_from(notif_query.subquery()))
    alerts_sent_30d = alerts_result.scalar_one()

    # Delivery rate (delivered / total sent, last 30 days)
    delivered_query = notif_query.where(Notification.status == NotificationStatus.delivered)
    delivered_result = await db.execute(select(func.count()).select_from(delivered_query.subquery()))
    delivered_count = delivered_result.scalar_one()
    delivery_rate = round(delivered_count / alerts_sent_30d, 2) if alerts_sent_30d else 0.0

    # Upcoming hearings in next 7 days
    today = date.today()
    in_7d = today + timedelta(days=7)
    upcoming_query = (
        select(func.count())
        .select_from(
            select(Hearing)
            .join(Registration, Hearing.registration_id == Registration.id)
            .where(
                Hearing.hearing_date >= today,
                Hearing.hearing_date <= in_7d,
                Hearing.is_completed == False,
                Registration.is_active == True,
            )
            .subquery()
        )
    )
    if current_user.role != UserRole.admin:
        upcoming_query = (
            select(func.count())
            .select_from(
                select(Hearing)
                .join(Registration, Hearing.registration_id == Registration.id)
                .where(
                    Hearing.hearing_date >= today,
                    Hearing.hearing_date <= in_7d,
                    Hearing.is_completed == False,
                    Registration.is_active == True,
                    Registration.registered_by == current_user.id,
                )
                .subquery()
            )
        )
    upcoming_result = await db.execute(upcoming_query)
    upcoming_7d = upcoming_result.scalar_one()

    return OverviewStats(
        total_cases=total_cases,
        active_cases=active_cases,
        alerts_sent_30d=alerts_sent_30d,
        delivery_rate=delivery_rate,
        upcoming_7d=upcoming_7d,
    )


# ---------------------------------------------------------------------------
# GET /stats/upcoming-hearings
# ---------------------------------------------------------------------------

@router.get("/upcoming-hearings", response_model=list[UpcomingHearing])
async def upcoming_hearings(
    db:           AsyncSession = Depends(get_db),
    current_user: User         = Depends(get_current_user),
):
    today = date.today()
    in_7d = today + timedelta(days=7)

    query = (
        select(Hearing, Registration)
        .join(Registration, Hearing.registration_id == Registration.id)
        .where(
            Hearing.hearing_date >= today,
            Hearing.hearing_date <= in_7d,
            Hearing.is_completed == False,
            Registration.is_active == True,
        )
        .order_by(Hearing.hearing_date.asc())
    )

    if current_user.role != UserRole.admin:
        query = query.where(Registration.registered_by == current_user.id)

    result = await db.execute(query)
    rows = result.fetchall()

    return [
        UpcomingHearing(
            case_id=str(reg.id),
            case_title=reg.case_title or reg.cnr_number,
            cnr_number=reg.cnr_number,
            hearing_date=hearing.hearing_date,
            days_until=(hearing.hearing_date - today).days,
            court_name=reg.court_name,
        )
        for hearing, reg in rows
    ]


# ---------------------------------------------------------------------------
# GET /stats/delivery-rate
# ---------------------------------------------------------------------------

@router.get("/delivery-rate", response_model=DeliveryRateStats)
async def delivery_rate(
    db:           AsyncSession = Depends(get_db),
    current_user: User         = Depends(get_current_user),
):
    base = (
        select(
            Notification.channel,
            Notification.status,
            func.count().label("cnt"),
        )
        .join(Registration, Notification.registration_id == Registration.id)
        .group_by(Notification.channel, Notification.status)
    )

    if current_user.role != UserRole.admin:
        base = base.where(Registration.registered_by == current_user.id)

    result = await db.execute(base)
    rows = result.fetchall()

    # Aggregate into per-channel buckets
    buckets: dict[str, dict] = {
        "whatsapp": {"sent": 0, "delivered": 0, "failed": 0},
        "sms":      {"sent": 0, "delivered": 0, "failed": 0},
        "telegram": {"sent": 0, "delivered": 0, "failed": 0},
    }

    for channel, s, cnt in rows:
        ch = channel.value if hasattr(channel, "value") else str(channel)
        if ch not in buckets:
            continue
        total_key = "sent"
        if s == NotificationStatus.delivered:
            buckets[ch]["delivered"] += cnt
        elif s == NotificationStatus.failed:
            buckets[ch]["failed"] += cnt
        buckets[ch]["sent"] += cnt

    def _make_channel(data: dict) -> ChannelStats:
        total = data["sent"]
        return ChannelStats(
            sent=total,
            delivered=data["delivered"],
            failed=data["failed"],
            rate=round(data["delivered"] / total, 2) if total else 0.0,
        )

    return DeliveryRateStats(
        whatsapp=_make_channel(buckets["whatsapp"]),
        sms=_make_channel(buckets["sms"]),
        telegram=_make_channel(buckets["telegram"]),
    )
