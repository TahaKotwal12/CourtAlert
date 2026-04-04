import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import UserRole

if TYPE_CHECKING:
    from app.models.registration import Registration


class User(Base):
    __tablename__ = "users"

    id:              Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email:           Mapped[str]       = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str]       = mapped_column(String(255), nullable=False)
    full_name:       Mapped[str]       = mapped_column(String(200), nullable=False)
    org_name:        Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    role:            Mapped[UserRole]  = mapped_column(Enum(UserRole, name="user_role"), nullable=False, default=UserRole.ngo_user)
    is_active:       Mapped[bool]      = mapped_column(Boolean, nullable=False, default=True)
    created_at:      Mapped[datetime]  = mapped_column(nullable=False, server_default=func.now())
    updated_at:      Mapped[datetime]  = mapped_column(nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    registrations: Mapped[List["Registration"]] = relationship("Registration", back_populates="registered_by_user", foreign_keys="Registration.registered_by")
