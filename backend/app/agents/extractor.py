import os

from app.schemas import EmailInput, JobApplication
from app.services.llm import get_llm
from app.services.sanitize import sanitize_text

SYSTEM_PROMPT = """Você extrai dados de e-mails e notificações de processos seletivos de tecnologia.

Regras:
- Use somente informações presentes no texto. Nunca invente empresa, cargo ou requisitos.
- Use "Indefinido" quando o e-mail não disser em que etapa a candidatura está. Isso inclui avisos
  como "há uma atualização", "você recebeu uma mensagem" ou "acesse a plataforma para ver", que
  só mandam abrir um link. Não deduza a etapa pelo fato de a candidatura existir.
- Use "Em Análise" somente se o texto disser que o perfil ou currículo está sendo analisado ou que
  foi aprovado em uma triagem.
- Use "Inscrito" quando o e-mail confirma ou lembra que a candidatura foi feita, inclusive quando
  ainda falta finalizá-la ou completar o cadastro.
- Se o e-mail diz que o processo foi encerrado ou que a candidatura não terá continuidade, o status
  é "Rejeitado", mesmo que o motivo seja um cadastro incompleto. Esta regra vale mais que a anterior.
- "key_requirements" lista os requisitos da vaga citados no texto. Se não houver, devolva lista vazia.
- "next_steps" descreve o próximo passo, se houver (ex.: prazo do teste, data da entrevista).
- "confidence" vai de 0 a 1 e indica o quão seguro você está da extração.
- Marcadores como [EMAIL], [URL] e [TELEFONE] foram colocados para proteger dados pessoais. Ignore-os.
"""

def extract_application(email: EmailInput) -> JobApplication:
    clean_text = sanitize_text(email.raw_text)

    llm = get_llm(model=os.getenv("GEMINI_EXTRACTOR_MODEL") or None).with_structured_output(JobApplication)
    return llm.invoke(
        [
            ("system", SYSTEM_PROMPT),
            ("human", clean_text),
        ]
    )