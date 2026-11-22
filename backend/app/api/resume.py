import traceback
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.optimizer import optimize_resume
from app.db import get_db
from app.demo import (
    check_size,
    demo_enabled,
    demo_scope,
    enforce_ai_limit,
    max_job_chars,
    max_pdf_bytes,
    max_resume_chars,
    scope_filter,
)
from app.models import ApplicationRecord, BaseResume
from app.schemas import OptimizeRequest, ResumeOptimization, ResumeRead, ResumeUpsert
from app.services.pdf import MAX_PDF_BYTES, PdfExtractionError, extract_text_from_pdf

router = APIRouter(tags=["resume"])


def get_resume(db: Session, session_id: Optional[str]) -> Optional[BaseResume]:
    """Um currículo base por dono (no uso normal, um só; na demonstração, um por visitante)."""
    return db.scalar(select(BaseResume).where(scope_filter(BaseResume.session_id, session_id)))


def job_text_from_application(record: ApplicationRecord) -> str:
    requirements = ", ".join(record.key_requirements) or "não informados"
    return (
        f"Cargo: {record.job_title}\n"
        f"Empresa: {record.company_name}\n"
        f"Requisitos citados: {requirements}"
    )


@router.get("/resume", response_model=ResumeRead)
def read_resume(db: Session = Depends(get_db), session_id: Optional[str] = Depends(demo_scope)):
    record = get_resume(db, session_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Nenhum currículo salvo ainda")
    return record


@router.put("/resume", response_model=ResumeRead)
def save_resume(
    payload: ResumeUpsert,
    db: Session = Depends(get_db),
    session_id: Optional[str] = Depends(demo_scope),
):
    check_size(payload.content, max_resume_chars(), "O currículo")
    record = get_resume(db, session_id)
    if record is None:
        record = BaseResume(session_id=session_id, content=payload.content)
        db.add(record)
    else:
        record.content = payload.content
    db.commit()
    db.refresh(record)
    return record


@router.post("/optimize", response_model=ResumeOptimization)
def optimize(
    payload: OptimizeRequest,
    db: Session = Depends(get_db),
    session_id: Optional[str] = Depends(demo_scope),
    _limit: None = Depends(enforce_ai_limit),
):
    resume = get_resume(db, session_id)
    if resume is None:
        raise HTTPException(status_code=409, detail="Salve seu currículo antes (PUT /resume)")

    if payload.job_description and payload.job_description.strip():
        check_size(payload.job_description, max_job_chars(), "A descrição da vaga")
        job_text = payload.job_description
    else:
        if not payload.application_id:
            raise HTTPException(status_code=400, detail="Informe 'job_description' ou 'application_id'.")
        record = db.get(ApplicationRecord, payload.application_id)
        if record is None or record.session_id != session_id:
            raise HTTPException(status_code=404, detail="Candidatura não encontrada")
        job_text = job_text_from_application(record)

    try:
        return optimize_resume(resume.content, job_text)
    except Exception as e:
        traceback.print_exc()
        detail = "Erro interno no processamento com a IA."
        if not demo_enabled():
            detail = f"{detail} {str(e)}"
        raise HTTPException(status_code=500, detail=detail)
        
@router.post("/resume/upload", response_model=ResumeRead)
async def upload_resume_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    session_id: Optional[str] = Depends(demo_scope),
):
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="O arquivo enviado deve ser no formato PDF.")

    # Lê no máximo 1 byte além do limite: arquivo enorme não ocupa a memória toda.
    limit = max_pdf_bytes() if demo_enabled() else MAX_PDF_BYTES
    content_bytes = await file.read(limit + 1)
    if demo_enabled() and len(content_bytes) > limit:
        raise HTTPException(
            status_code=400,
            detail=f"O PDF passa de {limit / 1_000_000:g} MB, o limite da demonstração.",
        )

    try:
        extracted_text = extract_text_from_pdf(content_bytes)
    except PdfExtractionError as exc:
        # A mensagem do serviço é segura para o usuário; HTTP é decidido aqui na rota.
        raise HTTPException(status_code=400, detail=str(exc)) from None

    if demo_enabled():
        extracted_text = extracted_text[: max_resume_chars()]

    record = get_resume(db, session_id)
    if record is None:
        record = BaseResume(session_id=session_id, content=extracted_text)
        db.add(record)
    else:
        record.content = extracted_text

    db.commit()
    db.refresh(record)
    return record