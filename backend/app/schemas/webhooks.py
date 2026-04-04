from typing import Optional
from pydantic import BaseModel


class TwilioStatusCallback(BaseModel):
    """Delivery status callback posted by Twilio."""
    MessageSid:    str
    MessageStatus: str  # delivered / failed / undelivered / sent / queued
    To:            Optional[str] = None
    From:          Optional[str] = None
