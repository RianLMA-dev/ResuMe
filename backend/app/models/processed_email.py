from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.application import utcnow


class ProcessedEmail(Base):
    __tablename__ = "processed_emails"

    id: Mapped[int] = mapped_column(primary_key=True)
    gmail_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    outcome: Mapped[str] = mapped_column(String(20))  # "saved" ou "discarded"
    application_id: Mapped[Optional[int]] = mapped_column(nullable=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)