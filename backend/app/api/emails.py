from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agents.graph import graph
from app.db import get_db
from app.schemas import ApplicationRead, EmailInput
from app.services.applications import upsert_application

router = APIRouter(prefix="/emails", tags=["emails"])


class EmailAnalysis(BaseModel):
    is_job_related: bool
    reason: str
    application: Optional[ApplicationRead] = None


@router.post("", response_model=EmailAnalysis)
def analyze_email(email: EmailInput, db: Session = Depends(get_db)):
    """Classifica o e-mail e, se for de vaga, extrai e salva a candidatura."""
    try:
        result = graph.invoke({"email": email})
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Falha ao processar o e-mail: {exc}")

    saved = None
    if result.get("application"):
        saved = ApplicationRead.model_validate(upsert_application(db, result["application"]))

    return EmailAnalysis(
        is_job_related=result["is_job_related"],
        reason=result["reason"],
        application=saved,
    )