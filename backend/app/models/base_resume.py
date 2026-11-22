from datetime import datetime

from typing import Optional

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.application import utcnow


class BaseResume(Base):
    __tablename__ = "base_resume"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    session_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )