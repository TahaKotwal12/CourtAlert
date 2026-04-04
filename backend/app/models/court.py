import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Court(Base):
    __tablename__ = "courts"

    id:            Mapped[uuid.UUID]        = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    state_code:    Mapped[str]              = mapped_column(String(10), nullable=False, index=True)
    district_code: Mapped[Optional[str]]   = mapped_column(String(10), nullable=True)
    court_name:    Mapped[str]             = mapped_column(String(255), nullable=False)
    address:       Mapped[Optional[str]]   = mapped_column(Text, nullable=True)
    latitude:      Mapped[Optional[Decimal]] = mapped_column(Numeric(9, 6), nullable=True)
    longitude:     Mapped[Optional[Decimal]] = mapped_column(Numeric(9, 6), nullable=True)
    pin_code:      Mapped[Optional[str]]   = mapped_column(String(10), nullable=True)
