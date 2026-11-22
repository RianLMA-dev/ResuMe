from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.demo import demo_scope, ensure_card_room, scope_filter
from app.models import ApplicationRecord
from app.schemas import ApplicationCreate, ApplicationRead, ApplicationUpdate

router = APIRouter(prefix="/applications", tags=["applications"])


def get_or_404(
    db: Session, application_id: int, session_id: Optional[str] = None
) -> ApplicationRecord:
    record = db.get(ApplicationRecord, application_id)
    if record is None or record.session_id != session_id:
        raise HTTPException(status_code=404, detail="Candidatura não encontrada")
    return record


@router.get("", response_model=List[ApplicationRead])
def list_applications(
    db: Session = Depends(get_db), session_id: Optional[str] = Depends(demo_scope)
):
    stmt = (
        select(ApplicationRecord)
        .where(scope_filter(ApplicationRecord.session_id, session_id))
        .order_by(ApplicationRecord.updated_at.desc())
    )
    return db.scalars(stmt).all()


@router.post("", response_model=ApplicationRead, status_code=201)
def create_application(
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
    session_id: Optional[str] = Depends(demo_scope),
):
    ensure_card_room(db, session_id)
    record = ApplicationRecord(
        session_id=session_id,
        company_name=payload.company_name,
        job_title=payload.job_title,
        status=payload.status.value,
        key_requirements=payload.key_requirements,
        next_steps=payload.next_steps,
        confidence=1.0,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.patch("/{application_id}", response_model=ApplicationRead)
def update_application(
    application_id: int,
    payload: ApplicationUpdate,
    db: Session = Depends(get_db),
    session_id: Optional[str] = Depends(demo_scope),
):
    record = get_or_404(db, application_id, session_id)

    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        if value is None and field != "next_steps":
            continue  # campos obrigatórios não aceitam null
        if field == "status":
            value = value.value
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return record


@router.delete("/{application_id}", status_code=204)
def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    session_id: Optional[str] = Depends(demo_scope),
):
    record = get_or_404(db, application_id, session_id)
    db.delete(record)
    db.commit()
    return Response(status_code=204)

