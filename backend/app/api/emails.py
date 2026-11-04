import re
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agents.graph import graph
from app.db import get_db
from app.schemas import ApplicationRead, EmailInput
from app.services.applications import upsert_application

router = APIRouter(prefix="/emails", tags=["emails"])

GENERIC_DOMAINS = {
    "gmail.com", "hotmail.com", "outlook.com", "yahoo.com", 
    "icloud.com", "live.com", "protonmail.com"
}


def extract_company_domain(sender_email: Optional[str]) -> Optional[str]:
    """Extrai o domínio limpo do e-mail do remetente ignorando webmails genéricos."""
    if not sender_email:
        return None
        
    match = re.search(r"@([\w.-]+)", sender_email.strip())
    if match:
        domain = match.group(1).lower()
        if domain not in GENERIC_DOMAINS:
            return domain
            
    return None


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

    time.sleep(4.5)

    saved = None
    if result.get("application"): 
        app_data = result["application"]
        
        # Extrai o domínio exato do remetente sem gastar tokens da IA
        domain = extract_company_domain(getattr(email, "sender_email", None))
        
        # Injeta o domínio no objeto/dicionário antes de salvar
        if isinstance(app_data, dict):
            app_data["company_domain"] = domain
        elif hasattr(app_data, "company_domain"):
            app_data.company_domain = domain

        saved = ApplicationRead.model_validate(upsert_application(db, app_data))

    return EmailAnalysis(
        is_job_related=result["is_job_related"],
        reason=result["reason"],
        application=saved,
    )