"""Modo demonstração: dados separados por visitante, limites de uso e sem Gmail.

Ligado só quando DEMO_MODE=true. Fora dele, nada neste módulo muda o comportamento do app
(session_id fica sempre NULL e os limites não existem).
"""
import hashlib
import os
import re
import secrets
import time
from datetime import timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Request
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.demo_seed import SAMPLE_CARDS, SAMPLE_RESUME
from app.models import ApplicationRecord, BaseResume, DemoSession, DemoUsage
from app.models.application import utcnow

SESSION_HEADER = "X-Demo-Session"
_SESSION_RE = re.compile(r"^[0-9a-fA-F-]{36}$")
_SALT = os.getenv("DEMO_SALT") or secrets.token_hex(16)
_PURGE_EVERY_SECONDS = 600
_last_purge = 0.0


def demo_enabled() -> bool:
    return os.getenv("DEMO_MODE", "").strip().lower() in {"1", "true", "yes", "on"}


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return default


def ttl_hours() -> int:
    return _int_env("DEMO_SESSION_TTL_HOURS", 6)


def ai_per_session_hour() -> int:
    return _int_env("DEMO_AI_PER_SESSION_HOUR", 12)


def ai_per_ip_hour() -> int:
    return _int_env("DEMO_AI_PER_IP_HOUR", 30)


def ai_per_day() -> int:
    return _int_env("DEMO_AI_PER_DAY", 300)


def max_cards() -> int:
    return _int_env("DEMO_MAX_CARDS", 30)


def max_email_chars() -> int:
    return _int_env("DEMO_MAX_EMAIL_CHARS", 6000)


def max_job_chars() -> int:
    return _int_env("DEMO_MAX_JOB_CHARS", 8000)


def max_resume_chars() -> int:
    return _int_env("DEMO_MAX_RESUME_CHARS", 12000)


def max_pdf_bytes() -> int:
    return _int_env("DEMO_MAX_PDF_BYTES", 1_000_000)


def trusted_proxies() -> int:
    return max(1, _int_env("DEMO_TRUSTED_PROXIES", 1))


def public_config() -> dict:
    return {
        "demo": demo_enabled(),
        "session_ttl_hours": ttl_hours(),
        "max_email_chars": max_email_chars(),
        "max_job_chars": max_job_chars(),
    }


def scope_filter(column, session_id: Optional[str]):
    """Filtro por visitante. Sem sessão (uso normal), pega só as linhas sem dono."""
    return column.is_(None) if session_id is None else column == session_id


# ---------- sessões, dados de exemplo e limpeza ----------


def _seed(db: Session, session_id: str) -> None:
    now = utcnow()
    for index, (company, title, status, requirements, next_steps) in enumerate(SAMPLE_CARDS):
        moment = now - timedelta(hours=index * 7 + 1)
        db.add(
            ApplicationRecord(
                session_id=session_id,
                company_name=company,
                job_title=title,
                status=status,
                key_requirements=requirements,
                next_steps=next_steps,
                confidence=0.95,
                created_at=moment,
                updated_at=moment,
            )
        )
    db.add(BaseResume(session_id=session_id, content=SAMPLE_RESUME))


def ensure_session(db: Session, session_id: str) -> None:
    purge_expired(db)
    if db.get(DemoSession, session_id) is not None:
        return
    db.add(DemoSession(session_id=session_id))
    _seed(db, session_id)
    try:
        db.commit()
    except IntegrityError:
        # Outra requisição do mesmo visitante criou a sessão primeiro (e já semeou os dados).
        db.rollback()


def purge_expired(db: Session, force: bool = False) -> None:
    """Apaga sessões vencidas com os seus dados, e contadores antigos. No máximo a cada 10 min."""
    global _last_purge
    if not force and time.monotonic() - _last_purge < _PURGE_EVERY_SECONDS:
        return
    _last_purge = time.monotonic()

    now = utcnow()
    expired = select(DemoSession.session_id).where(
        DemoSession.created_at < now - timedelta(hours=ttl_hours())
    )
    db.execute(delete(ApplicationRecord).where(ApplicationRecord.session_id.in_(expired)))
    db.execute(delete(BaseResume).where(BaseResume.session_id.in_(expired)))
    db.execute(
        delete(DemoSession).where(DemoSession.created_at < now - timedelta(hours=ttl_hours()))
    )
    db.execute(
        delete(DemoUsage).where(
            DemoUsage.scope != "day", DemoUsage.window < _hour_key(now - timedelta(hours=3))
        )
    )
    db.execute(
        delete(DemoUsage).where(
            DemoUsage.scope == "day", DemoUsage.window < _day_key(now - timedelta(days=2))
        )
    )
    db.commit()


# ---------- dependências das rotas ----------


def demo_scope(request: Request, db: Session = Depends(get_db)) -> Optional[str]:
    """Identifica o visitante. Fora da demonstração devolve None e não faz nada."""
    if not demo_enabled():
        return None
    session_id = request.headers.get(SESSION_HEADER, "")
    if not _SESSION_RE.match(session_id):
        raise HTTPException(
            status_code=400,
            detail="Sessão da demonstração ausente ou inválida. Recarregue a página.",
        )
    session_id = session_id.lower()
    ensure_session(db, session_id)
    return session_id


def block_in_demo() -> None:
    if demo_enabled():
        raise HTTPException(
            status_code=403,
            detail="O Gmail não está disponível na demonstração. Rode o projeto na sua máquina para usá-lo.",
        )


def _hour_key(moment) -> str:
    return moment.strftime("%Y%m%d%H")


def _day_key(moment) -> str:
    return moment.strftime("%Y%m%d")


def _client_hash(request: Request) -> str:
    forwarded = [p.strip() for p in request.headers.get("x-forwarded-for", "").split(",") if p.strip()]
    hops = trusted_proxies()
    if len(forwarded) >= hops:
        ip = forwarded[-hops]  # o proxy da hospedagem acrescenta o IP real no fim da lista
    else:
        ip = request.client.host if request.client else "desconhecido"
    return hashlib.sha256(f"{_SALT}{ip}".encode()).hexdigest()[:32]


def enforce_ai_limit(
    request: Request,
    db: Session = Depends(get_db),
    session_id: Optional[str] = Depends(demo_scope),
) -> None:
    """Conta um uso da IA por sessão, por rede e por dia. Passou do limite: 429."""
    if not demo_enabled():
        return

    now = utcnow()
    hour, day = _hour_key(now), _day_key(now)
    until_next_hour = 3600 - (now.minute * 60 + now.second)
    until_next_day = 86400 - (now.hour * 3600 + now.minute * 60 + now.second)
    checks = [
        ("session", session_id or "", hour, ai_per_session_hour(), until_next_hour,
         "Você usou todas as análises por hora da demonstração. Tente de novo mais tarde."),
        ("ip", _client_hash(request), hour, ai_per_ip_hour(), until_next_hour,
         "Muitas análises vindas da sua rede nesta hora. Tente de novo mais tarde."),
        ("day", "all", day, ai_per_day(), until_next_day,
         "A demonstração atingiu o limite de uso de hoje. Volte amanhã ou rode o projeto na sua máquina."),
    ]

    rows = []
    for scope, key, window, limit, retry_after, message in checks:
        row = db.scalar(
            select(DemoUsage).where(
                DemoUsage.scope == scope, DemoUsage.key == key, DemoUsage.window == window
            )
        )
        if row is not None and row.count >= limit:
            raise HTTPException(
                status_code=429, detail=message, headers={"Retry-After": str(retry_after)}
            )
        rows.append((scope, key, window, row))

    for scope, key, window, row in rows:
        if row is None:
            db.add(DemoUsage(scope=scope, key=key, window=window, count=1))
        else:
            row.count += 1
    db.commit()


def ensure_card_room(db: Session, session_id: Optional[str]) -> None:
    if not demo_enabled():
        return
    total = db.scalar(
        select(func.count()).select_from(ApplicationRecord).where(
            ApplicationRecord.session_id == session_id
        )
    )
    if total >= max_cards():
        raise HTTPException(
            status_code=409,
            detail=f"A demonstração aceita até {max_cards()} cartões por visitante. Apague algum para continuar.",
        )


def check_size(text: str, limit: int, what: str) -> None:
    if demo_enabled() and len(text) > limit:
        raise HTTPException(
            status_code=413,
            detail=f"{what} passa do limite da demonstração ({limit} caracteres).",
        )
