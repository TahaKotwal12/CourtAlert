import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Enum, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import ChannelType, NotificationStatus

if TYPE_CHECKING:
    from app.models.registration import Registration
    from app.models.hearing import Hearing


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        UniqueConstraint("registration_id", "hearing_id", "days_before", name="idx_notif_unique"),
    )

    id:               Mapped[uuid.UUID]          = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    registration_id:  Mapped[uuid.UUID]          = mapped_column(UUID(as_uuid=True), ForeignKey("registrations.id", ondelete="CASCADE"), nullable=False)
    hearing_id:       Mapped[uuid.UUID]          = mapped_column(UUID(as_uuid=True), ForeignKey("hearings.id", ondelete="CASCADE"), nullable=False)
    channel:          Mapped[ChannelType]        = mapped_column(Enum(ChannelType, name="channel_type"), nullable=False)
    status:           Mapped[NotificationStatus] = mapped_column(Enum(NotificationStatus, name="notification_status"), nullable=False, default=NotificationStatus.sent, index=True)
    message_text:     Mapped[str]                = mapped_column(Text, nullable=False)
    message_language: Mapped[str]                = mapped_column(String(5), nullable=False)
    days_before:      Mapped[int]                = mapped_column(Integer, nullable=False)
    twilio_sid:       Mapped[Optional[str]]      = mapped_column(String(50), nullable=True)
    error_message:    Mapped[Optional[str]]      = mapped_column(Text, nullable=True)
    sent_at:          Mapped[datetime]           = mapped_column(nullable=False, server_default=func.now())
    delivered_at:     Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationships
    registration: Mapped["Registration"] = relationship("Registration", back_populates="notifications")
    hearing:      Mapped["Hearing"]      = relationship("Hearing", back_populates="notifications")
