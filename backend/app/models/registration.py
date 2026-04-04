import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.hearing import Hearing
    from app.models.notification import Notification
    from app.models.whatsapp_command import WhatsappCommand


class Registration(Base):
    __tablename__ = "registrations"

    id:             Mapped[uuid.UUID]      = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cnr_number:     Mapped[str]            = mapped_column(String(20), nullable=False, index=True)
    phone_number:   Mapped[str]            = mapped_column(String(15), nullable=False, index=True)
    language:       Mapped[str]            = mapped_column(String(5), nullable=False, default="hi")
    case_title:     Mapped[Optional[str]]  = mapped_column(Text, nullable=True)
    court_name:     Mapped[Optional[str]]  = mapped_column(String(255), nullable=True)
    state_code:     Mapped[Optional[str]]  = mapped_column(String(10), nullable=True)
    district_code:  Mapped[Optional[str]]  = mapped_column(String(10), nullable=True)
    is_active:      Mapped[bool]           = mapped_column(Boolean, nullable=False, default=True)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    registered_by:  Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at:     Mapped[datetime]       = mapped_column(nullable=False, server_default=func.now())

    # Relationships
    registered_by_user: Mapped[Optional["User"]]              = relationship("User", back_populates="registrations", foreign_keys=[registered_by])
    hearings:           Mapped[List["Hearing"]]               = relationship("Hearing", back_populates="registration", cascade="all, delete-orphan")
    notifications:      Mapped[List["Notification"]]          = relationship("Notification", back_populates="registration", cascade="all, delete-orphan")
    whatsapp_commands:  Mapped[List["WhatsappCommand"]]       = relationship("WhatsappCommand", back_populates="registration")
