from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.optimizer import optimize_resume
from app.db import get_db
from app.models import ApplicationRecord, BaseResume
from app.schemas import OptimizeRequest, ResumeOptimization, ResumeRead, ResumeUpsert

router = APIRouter(tags=["resume"])

RESUME_ID = 1  # por enquanto, um único currículo base


def job_text_from_application(record: ApplicationRecord) -> str:
    requirements = ", ".join(record.key_requirements) or "não informados"
    return (
        f"Cargo: {record.job_title}\n"
        f"Empresa: {record.company_name}\n"
        f"Requisitos citados: {requirements}"
    )


@router.get("/resume", response_model=ResumeRead)
def read_resume(db: Session = Depends(get_db)):
    record = db.get(BaseResume, RESUME_ID)
    if record is None:
        raise HTTPException(status_code=404, detail="Nenhum currículo salvo ainda")
    return record


@router.put("/resume", response_model=ResumeRead)
def save_resume(payload: ResumeUpsert, db: Session = Depends(get_db)):
    record = db.get(BaseResume, RESUME_ID)
    if record is None:
        record = BaseResume(id=RESUME_ID, content=payload.content)
        db.add(record)
    else:
        record.content = payload.content
    db.commit()
    db.refresh(record)
    return record


@router.post("/optimize", response_model=ResumeOptimization)
def optimize(payload: OptimizeRequest, db: Session = Depends(get_db)):
    resume = db.get(BaseResume, RESUME_ID)
    if resume is None:
        raise HTTPException(status_code=409, detail="Salve seu currículo antes (PUT /resume)")

    if payload.job_description and payload.job_description.strip():
        job_text = payload.job_description
    else:
        record = db.get(ApplicationRecord, payload.application_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Candidatura não encontrada")
        job_text = job_text_from_application(record)

    try:
        return optimize_resume(resume.content, job_text)
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="A IA não conseguiu analisar agora. Pode ser o limite do Gemini: tente em um minuto.",
        )