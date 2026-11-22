from datetime import datetime

from sqlalchemy import DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.application import utcnow


class DemoSession(Base):
    """Um visitante da demonstração pública. Some junto com os seus dados depois do prazo."""

    __tablename__ = "demo_sessions"

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class DemoUsage(Base):
    """Contador de usos da IA na demonstração, por sessão, por rede (hash) e por dia."""

    __tablename__ = "demo_usage"
    __table_args__ = (UniqueConstraint("scope", "key", "window", name="uq_demo_usage"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    scope: Mapped[str] = mapped_column(String(16))
    key: Mapped[str] = mapped_column(String(64))
    window: Mapped[str] = mapped_column(String(16))
    count: Mapped[int] = mapped_column(Integer, default=0)
