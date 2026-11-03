from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ResumeUpsert(BaseModel):
    content: str = Field(min_length=50, max_length=30000)


class ResumeRead(BaseModel):
    content: str
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OptimizeRequest(BaseModel):
    application_id: Optional[int] = None
    job_description: Optional[str] = Field(default=None, max_length=20000)

    @model_validator(mode="after")
    def require_a_job(self):
        has_text = bool(self.job_description and self.job_description.strip())
        if not has_text and self.application_id is None:
            raise ValueError("Envie application_id ou job_description")
        return self