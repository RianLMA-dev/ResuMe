from pydantic import BaseModel, Field

from app.schemas import EmailInput
from app.services.llm import get_llm
from app.services.sanitize import sanitize_text

SYSTEM_PROMPT = """Você classifica e-mails.
Responda is_job_related=true apenas se o e-mail for sobre um processo seletivo
de emprego em que o destinatário é candidato (inscrição, triagem, teste técnico,
entrevista, proposta ou rejeição). Newsletters, alertas genéricos de vagas,
propagandas e spam são false.
Em "reason", explique em uma frase curta."""


class EmailClassification(BaseModel):
    is_job_related: bool
    reason: str = Field(description="Justificativa curta")


def classify_email(email: EmailInput) -> EmailClassification:
    clean_text = sanitize_text(email.raw_text)
    llm = get_llm().with_structured_output(EmailClassification)
    return llm.invoke(
        [
            ("system", SYSTEM_PROMPT),
            ("human", clean_text),
        ]
    )