from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

class ApplicationStatus(str, Enum):
    APPLIED = "Inscrito"
    IN_REVIEW = "Em Análise"
    TECHNICAL_TEST = "Teste Técnico"
    INTERVIEW = "Entrevista"
    OFFER = "Oferta"
    REJECTED = "Rejeitado"
    UNKNOWN = "Indefinido"


class EmailInput(BaseModel):
    raw_text: str = Field(min_length=10)


class JobApplication(BaseModel):
    company_name: str
    job_title: str
    status: ApplicationStatus
    key_requirements: List[str] = Field(default_factory=list)
    next_steps: Optional[str] = None
    confidence: float = Field(ge=0, le=1, description="Confiança da extração")


class ResumeOptimization(BaseModel):
    matching_score: int = Field(ge=0, le=100)
    missing_keywords: List[str]
    suggested_bullet_points: List[str]

class ApplicationRead(JobApplication):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True) 
    
class ApplicationCreate(BaseModel):
    company_name: str = Field(min_length=1)
    job_title: str = Field(min_length=1)
    status: ApplicationStatus = ApplicationStatus.APPLIED
    key_requirements: List[str] = Field(default_factory=list)
    next_steps: Optional[str] = None


class ApplicationUpdate(BaseModel):
    company_name: Optional[str] = Field(default=None, min_length=1)
    job_title: Optional[str] = Field(default=None, min_length=1)
    status: Optional[ApplicationStatus] = None
    key_requirements: Optional[List[str]] = None
    next_steps: Optional[str] = None    