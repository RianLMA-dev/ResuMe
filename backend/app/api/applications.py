from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import ApplicationRecord
from app.schemas import ApplicationCreate, ApplicationRead, ApplicationUpdate

router = APIRouter(prefix="/applications", tags=["applications"])


def get_or_404(db: Session, application_id: int) -> ApplicationRecord:
    record = db.get(ApplicationRecord, application_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Candidatura não encontrada")
    return record


@router.get("", response_model=List[ApplicationRead])
def list_applications(db: Session = Depends(get_db)):
    stmt = select(ApplicationRecord).order_by(ApplicationRecord.updated_at.desc())
    return db.scalars(stmt).all()


@router.post("", response_model=ApplicationRead, status_code=201)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)):
    record = ApplicationRecord(
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
    application_id: int, payload: ApplicationUpdate, db: Session = Depends(get_db)
):
    record = get_or_404(db, application_id)

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
def delete_application(application_id: int, db: Session = Depends(get_db)):
    record = get_or_404(db, application_id)
    db.delete(record)
    db.commit()
    return Response(status_code=204)