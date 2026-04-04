import csv
import io
import math
import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.enums import UserRole
from app.models.hearing import Hearing
from app.models.notification import Notification
from app.models.registration import Registration
from app.models.user import User
from app.schemas.cases import (
    BulkUploadError,
    BulkUploadResponse,
    CaseDetailOut,
    CaseOut,
    CasesListResponse,
    HearingOut,
    RegisterCaseRequest,
    RegisterCaseResponse,
    SyncResponse,
)
from app.services import ecourts

router = APIRouter(prefix="/cases", tags=["Cases"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _next_hearing(hearings: list[Hearing]) -> Optional[date]:
    today = date.today()
    upcoming = [h.hearing_date for h in hearings if not h.is_completed and h.hearing_date >= today]
    return min(upcoming) if upcoming else None


async def _sync_case(registration: Registration, db: AsyncSession) -> int:
    """
    Pull latest hearing data from eCourts (mock) and upsert into hearings table.
    Returns count of hearings inserted/updated.
    """
    data = await ecourts.fetch_case(registration.cnr_number)
    if not data:
        return 0

    # Update case metadata from eCourts response
    registration.case_title  = data["case_title"]
    registration.court_name  = data["court_name"]
    registration.state_code  = data["state_code"]
    registration.district_code = data["district_code"]
    registration.last_synced_at = func.now()

    # Fetch existing hearing dates to avoid duplicates
    result = await db.execute(
        select(Hearing.hearing_date).where(Hearing.registration_id == registration.id)
    )
    existing_dates = {row[0] for row in result.fetchall()}

    count = 0
    for h in data["hearings"]:
        if h["hearing_date"] not in existing_dates:
            db.add(Hearing(
                registration_id=registration.id,
                hearing_date=h["hearing_date"],
                hearing_type=h.get("hearing_type"),
                court_room=h.get("court_room"),
                judge_name=h.get("judge_name"),
                purpose=h.get("purpose"),
                is_completed=h.get("is_completed", False),
            ))
            count += 1

    return count


async def _register_single_case(
    cnr: str,
    phone: str,
    language: str,
    registered_by_id: Optional[uuid.UUID],
    db: AsyncSession,
) -> tuple[Optional[Registration], Optional[str]]:
    """
    Core registration logic used by both single and bulk endpoints.
    Returns (registration, error_reason) — one of them is always None.
    """
    # Validate CNR via eCourts service
    case_data = await ecourts.fetch_case(cnr)
    if not case_data:
        return None, f"CNR {cnr} not found or invalid format"

    # Check duplicate: same CNR + same phone already active
    dup = await db.execute(
        select(Registration).where(
            Registration.cnr_number == cnr,
            Registration.phone_number == phone,
            Registration.is_active == True,
        )
    )
    if dup.scalar_one_or_none():
        return None, f"CNR {cnr} is already registered for this phone number"

    reg = Registration(
        cnr_number=cnr,
        phone_number=phone,
        language=language,
        case_title=case_data["case_title"],
        court_name=case_data["court_name"],
        state_code=case_data["state_code"],
        district_code=case_data["district_code"],
        registered_by=registered_by_id,
    )
    db.add(reg)
    await db.flush()  # get UUID

    # Insert hearings
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

    return reg, None


# ---------------------------------------------------------------------------
# POST /cases/register
# ---------------------------------------------------------------------------

@router.post("/register", response_model=RegisterCaseResponse, status_code=status.HTTP_201_CREATED)
async def register_case(
    payload: RegisterCaseRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reg, error = await _register_single_case(
        cnr=payload.cnr_number,
        phone=payload.phone_number,
        language=payload.language,
        registered_by_id=current_user.id,
        db=db,
    )
    if error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error)

    # Load hearings to compute next_hearing
    result = await db.execute(select(Hearing).where(Hearing.registration_id == reg.id))
    hearings = result.scalars().all()

    return RegisterCaseResponse(
        id=reg.id,
        cnr_number=reg.cnr_number,
        case_title=reg.case_title,
        next_hearing=_next_hearing(list(hearings)),
    )


# ---------------------------------------------------------------------------
# GET /cases
# ---------------------------------------------------------------------------

@router.get("", response_model=CasesListResponse)
async def list_cases(
    page:      int            = Query(default=1, ge=1),
    limit:     int            = Query(default=20, ge=1, le=100),
    is_active: Optional[bool] = Query(default=None),
    search:    Optional[str]  = Query(default=None),
    db:        AsyncSession   = Depends(get_db),
    current_user: User        = Depends(get_current_user),
):
    query = select(Registration)

    # Scope: NGO users see only their own registrations
    if current_user.role != UserRole.admin:
        query = query.where(Registration.registered_by == current_user.id)

    if is_active is not None:
        query = query.where(Registration.is_active == is_active)

    if search:
        term = f"%{search}%"
        query = query.where(
            or_(
                Registration.cnr_number.ilike(term),
                Registration.case_title.ilike(term),
            )
        )

    # Total count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()

    # Paginate
    offset = (page - 1) * limit
    result = await db.execute(
        query.order_by(Registration.created_at.desc()).offset(offset).limit(limit)
    )
    registrations = result.scalars().all()

    # Compute next_hearing per case (load hearings for each)
    items = []
    for reg in registrations:
        h_result = await db.execute(select(Hearing).where(Hearing.registration_id == reg.id))
        hearings = h_result.scalars().all()
        case_out = CaseOut.model_validate(reg)
        case_out.next_hearing = _next_hearing(list(hearings))
        items.append(case_out)

    return CasesListResponse(
        items=items,
        total=total,
        page=page,
        pages=math.ceil(total / limit) if total else 1,
    )


# ---------------------------------------------------------------------------
# GET /cases/{id}
# ---------------------------------------------------------------------------

@router.get("/{case_id}", response_model=CaseDetailOut)
async def get_case(
    case_id:      uuid.UUID,
    db:           AsyncSession = Depends(get_db),
    current_user: User         = Depends(get_current_user),
):
    result = await db.execute(
        select(Registration)
        .options(
            selectinload(Registration.hearings),
            selectinload(Registration.notifications),
        )
        .where(Registration.id == case_id)
    )
    reg = result.scalar_one_or_none()

    if not reg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    # NGO users can only view their own cases
    if current_user.role != UserRole.admin and reg.registered_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    hearings      = sorted(reg.hearings, key=lambda h: h.hearing_date, reverse=True)
    notifications = sorted(reg.notifications, key=lambda n: n.sent_at, reverse=True)[:10]

    out = CaseDetailOut.model_validate(reg)
    out.next_hearing  = _next_hearing(reg.hearings)
    out.hearings      = [HearingOut.model_validate(h) for h in hearings]
    out.notifications = [n for n in notifications]
    return out


# ---------------------------------------------------------------------------
# DELETE /cases/{id}   (soft delete)
# ---------------------------------------------------------------------------

@router.delete("/{case_id}")
async def deactivate_case(
    case_id:      uuid.UUID,
    db:           AsyncSession = Depends(get_db),
    current_user: User         = Depends(get_current_user),
):
    result = await db.execute(select(Registration).where(Registration.id == case_id))
    reg = result.scalar_one_or_none()

    if not reg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    if current_user.role != UserRole.admin and reg.registered_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    reg.is_active = False
    return {"message": "Case deactivated. No further alerts will be sent."}


# ---------------------------------------------------------------------------
# POST /cases/{id}/sync
# ---------------------------------------------------------------------------

@router.post("/{case_id}/sync", response_model=SyncResponse)
async def sync_case(
    case_id:      uuid.UUID,
    db:           AsyncSession = Depends(get_db),
    current_user: User         = Depends(get_current_user),
):
    result = await db.execute(select(Registration).where(Registration.id == case_id))
    reg = result.scalar_one_or_none()

    if not reg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    if current_user.role != UserRole.admin and reg.registered_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    hearings_updated = await _sync_case(reg, db)

    # Reload hearings to compute next_hearing
    h_result = await db.execute(select(Hearing).where(Hearing.registration_id == reg.id))
    hearings = h_result.scalars().all()

    return SyncResponse(
        synced=True,
        hearings_updated=hearings_updated,
        next_hearing=_next_hearing(list(hearings)),
    )


# ---------------------------------------------------------------------------
# POST /cases/bulk-upload
# ---------------------------------------------------------------------------

@router.post("/bulk-upload", response_model=BulkUploadResponse)
async def bulk_upload(
    file:         UploadFile    = File(...),
    db:           AsyncSession  = Depends(get_db),
    current_user: User          = Depends(get_current_user),
):
    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be UTF-8 encoded CSV")

    reader = csv.DictReader(io.StringIO(text))
    required_cols = {"cnr_number", "phone_number", "language"}

    if not reader.fieldnames or not required_cols.issubset(set(reader.fieldnames)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CSV must have columns: {', '.join(sorted(required_cols))}",
        )

    rows = list(reader)
    if len(rows) > 500:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum 500 rows per upload")

    success_count = 0
    errors: list[BulkUploadError] = []

    for i, row in enumerate(rows, start=2):  # row 1 is header
        cnr      = row.get("cnr_number", "").strip().upper()
        phone    = row.get("phone_number", "").strip()
        language = row.get("language", "hi").strip().lower()

        if not cnr or not phone:
            errors.append(BulkUploadError(row=i, reason="cnr_number and phone_number are required"))
            continue

        if language not in {"hi", "mr", "te", "ta", "kn", "en"}:
            language = "hi"

        if not phone.startswith("+"):
            phone = "+91" + phone.lstrip("0")

        _, error = await _register_single_case(
            cnr=cnr,
            phone=phone,
            language=language,
            registered_by_id=current_user.id,
            db=db,
        )

        if error:
            errors.append(BulkUploadError(row=i, reason=error))
        else:
            success_count += 1

    return BulkUploadResponse(
        total=len(rows),
        success=success_count,
        failed=len(errors),
        errors=errors,
    )


# ---------------------------------------------------------------------------
# GET /cases/{id}/hearings
# ---------------------------------------------------------------------------

@router.get("/{case_id}/hearings", response_model=list[HearingOut])
async def get_case_hearings(
    case_id:       uuid.UUID,
    upcoming_only: bool         = Query(default=False),
    db:            AsyncSession = Depends(get_db),
    current_user:  User         = Depends(get_current_user),
):
    # Verify case exists and user has access
    result = await db.execute(select(Registration).where(Registration.id == case_id))
    reg = result.scalar_one_or_none()

    if not reg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    if current_user.role != UserRole.admin and reg.registered_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    query = select(Hearing).where(Hearing.registration_id == case_id)
    if upcoming_only:
        query = query.where(Hearing.hearing_date >= date.today(), Hearing.is_completed == False)

    h_result = await db.execute(query.order_by(Hearing.hearing_date.desc()))
    return h_result.scalars().all()
