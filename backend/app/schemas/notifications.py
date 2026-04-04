import uuid
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.enums import ChannelType, NotificationStatus


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

class TestNotificationRequest(BaseModel):
    phone_number: str  = Field(min_length=10, max_length=15)
    language:     str  = Field(default="hi")


class GenerateMessageRequest(BaseModel):
    case_title:   str  = Field(examples=["Sharma vs State of Maharashtra"])
    hearing_date: date = Field(examples=["2026-04-11"])
    court_name:   str  = Field(examples=["Bombay High Court"])
    court_room:   str  = Field(default="—", examples=["Court Room 3"])
    language:     str  = Field(default="hi", examples=["hi"])
    days_before:  int  = Field(default=7, examples=[7])


class GenerateMessageResponse(BaseModel):
    message:  str
    language: str
    source:   str  # "llm" or "template"


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

class NotificationListItem(BaseModel):
    id:               uuid.UUID
    registration_id:  uuid.UUID
    hearing_id:       uuid.UUID
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


class NotificationsListResponse(BaseModel):
    items: List[NotificationListItem]
    total: int


class TestNotificationResponse(BaseModel):
    status:     str
    channel:    str
    message_id: Optional[str] = None
