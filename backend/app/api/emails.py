from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents.graph import graph
from app.schemas import EmailInput, JobApplication

router = APIRouter(prefix="/emails", tags=["emails"])


class EmailAnalysis(BaseModel):
    is_job_related: bool
    reason: str
    application: Optional[JobApplication] = None


@router.post("", response_model=EmailAnalysis)
def analyze_email(email: EmailInput):
    try:
        result = graph.invoke({"email": email})
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Falha ao processar o e-mail: {exc}")

    return EmailAnalysis(
        is_job_related=result["is_job_related"],
        reason=result["reason"],
        application=result.get("application"),
    )