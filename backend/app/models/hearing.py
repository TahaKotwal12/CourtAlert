import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Date, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.registration import Registration
    from app.models.notification import Notification


class Hearing(Base):
    __tablename__ = "hearings"

    id:              Mapped[uuid.UUID]     = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    registration_id: Mapped[uuid.UUID]    = mapped_column(UUID(as_uuid=True), ForeignKey("registrations.id", ondelete="CASCADE"), nullable=False, index=True)
    hearing_date:    Mapped[date]          = mapped_column(Date, nullable=False, index=True)
    hearing_type:    Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    court_room:      Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    judge_name:      Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    purpose:         Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_completed:    Mapped[bool]          = mapped_column(Boolean, nullable=False, default=False)
    fetched_at:      Mapped[datetime]      = mapped_column(nullable=False, server_default=func.now())

    # Relationships
    registration:  Mapped["Registration"]       = relationship("Registration", back_populates="hearings")
    notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="hearing", cascade="all, delete-orphan")
