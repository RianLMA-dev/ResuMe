from app.schemas import EmailInput, JobApplication
from app.services.llm import get_llm
from app.services.sanitize import sanitize_text

SYSTEM_PROMPT = """Você extrai dados de e-mails e notificações de processos seletivos de tecnologia.

Regras:
- Use somente informações presentes no texto. Nunca invente empresa, cargo ou requisitos.
- Se o e-mail não indicar claramente o status, use "Indefinido".
- "key_requirements" lista os requisitos da vaga citados no texto. Se não houver, devolva lista vazia.
- "next_steps" descreve o próximo passo, se houver (ex.: prazo do teste, data da entrevista).
- "confidence" vai de 0 a 1 e indica o quão seguro você está da extração.
- Marcadores como [EMAIL], [URL] e [TELEFONE] foram colocados para proteger dados pessoais. Ignore-os.
"""

def extract_application(email: EmailInput) -> JobApplication:
    clean_text = sanitize_text(email.raw_text)

    llm = get_llm().with_structured_output(JobApplication)
    return llm.invoke(
        [
            ("system", SYSTEM_PROMPT),
            ("human", clean_text),
        ]
    )