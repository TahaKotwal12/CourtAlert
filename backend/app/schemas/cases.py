import uuid
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.enums import ChannelType, NotificationStatus


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

VALID_LANGUAGES = {"hi", "mr", "te", "ta", "kn", "en"}


class RegisterCaseRequest(BaseModel):
    cnr_number:   str = Field(min_length=10, max_length=20)
    phone_number: str = Field(min_length=10, max_length=15)
    language:     str = Field(default="hi")

    @field_validator("cnr_number")
    @classmethod
    def cnr_uppercase(cls, v: str) -> str:
        return v.upper().strip()

    @field_validator("phone_number")
    @classmethod
    def phone_e164(cls, v: str) -> str:
        v = v.strip()
        if not v.startswith("+"):
            v = "+91" + v.lstrip("0")
        return v

    @field_validator("language")
    @classmethod
    def valid_language(cls, v: str) -> str:
        v = v.lower().strip()
        if v not in VALID_LANGUAGES:
            raise ValueError(f"Language must be one of: {', '.join(sorted(VALID_LANGUAGES))}")
        return v


# ---------------------------------------------------------------------------
# Nested response schemas
# ---------------------------------------------------------------------------

class HearingOut(BaseModel):
    id:           uuid.UUID
    hearing_date: date
    hearing_type: Optional[str]
    court_room:   Optional[str]
    judge_name:   Optional[str]
    purpose:      Optional[str]
    is_completed: bool
    fetched_at:   datetime

    model_config = {"from_attributes": True}


class NotificationOut(BaseModel):
    id:               uuid.UUID
    channel:          ChannelType
    status:           NotificationStatus
    message_text:     str
    message_language: str
    days_before:      int
    twilio_sid:       Optional[str]
    error_message:    Optional[str]
    sent_at:          datetime
    delivered_at:     Optional[datetime]

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Case response schemas
# ---------------------------------------------------------------------------

class CaseOut(BaseModel):
    id:             uuid.UUID
    cnr_number:     str
    phone_number:   str
    language:       str
    case_title:     Optional[str]
    court_name:     Optional[str]
    state_code:     Optional[str]
    district_code:  Optional[str]
    is_active:      bool
    last_synced_at: Optional[datetime]
    created_at:     datetime
    next_hearing:   Optional[date] = None   # computed, not a DB column

    model_config = {"from_attributes": True}


class CaseDetailOut(CaseOut):
    hearings:      List[HearingOut]
    notifications: List[NotificationOut]


class CasesListResponse(BaseModel):
    items: List[CaseOut]
    total: int
    page:  int
    pages: int


# ---------------------------------------------------------------------------
# Register response
# ---------------------------------------------------------------------------

class RegisterCaseResponse(BaseModel):
    id:           uuid.UUID
    cnr_number:   str
    case_title:   Optional[str]
    next_hearing: Optional[date]

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Sync response
# ---------------------------------------------------------------------------

class SyncResponse(BaseModel):
    synced:           bool
    hearings_updated: int
    next_hearing:     Optional[date]


# ---------------------------------------------------------------------------
# Bulk upload
# ---------------------------------------------------------------------------

class BulkUploadError(BaseModel):
    row:    int
    reason: str


class BulkUploadResponse(BaseModel):
    total:   int
    success: int
    failed:  int
    errors:  List[BulkUploadError]
