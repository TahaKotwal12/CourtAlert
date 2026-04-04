import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import CommandType

if TYPE_CHECKING:
    from app.models.registration import Registration


class WhatsappCommand(Base):
    __tablename__ = "whatsapp_commands"

    id:                 Mapped[uuid.UUID]           = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_number:        Mapped[str]                 = mapped_column(String(20), nullable=False)
    body:               Mapped[str]                 = mapped_column(Text, nullable=False)
    command_type:       Mapped[Optional[CommandType]] = mapped_column(Enum(CommandType, name="command_type"), nullable=True)
    cnr_extracted:      Mapped[Optional[str]]       = mapped_column(String(20), nullable=True)
    language_extracted: Mapped[Optional[str]]       = mapped_column(String(5), nullable=True)
    registration_id:    Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("registrations.id", ondelete="SET NULL"), nullable=True)
    response_sent:      Mapped[Optional[str]]       = mapped_column(Text, nullable=True)
    twilio_sid:         Mapped[Optional[str]]       = mapped_column(String(50), nullable=True)
    received_at:        Mapped[datetime]            = mapped_column(nullable=False, server_default=func.now())

    # Relationships
    registration: Mapped[Optional["Registration"]] = relationship("Registration", back_populates="whatsapp_commands")
