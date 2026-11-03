from app.schemas import ResumeOptimization
from app.services.llm import get_groq_llm  
from app.services.sanitize import sanitize_text

SYSTEM_PROMPT = """Você ajuda a adaptar um currículo a uma vaga.

Receberá o CURRÍCULO e a VAGA. Responda com:
- matching_score: nota de 0 a 100 de quanto o currículo atende aos requisitos da vaga.
  É uma estimativa: seja realista e não infle a nota.
- missing_keywords: tecnologias, ferramentas e termos pedidos pela vaga que NÃO aparecem
  no currículo. Se o currículo já tem o termo, não liste.
- suggested_bullet_points: até 5 sugestões de frases para o currículo.

Regras importantes:
- Nunca invente experiência, projeto, cargo, empresa, número ou resultado que não esteja
  no currículo.
- Cada sugestão deve reescrever ou destacar algo que o currículo JÁ diz, usando as
  palavras da vaga apenas quando forem verdadeiras para essa pessoa.
- Se faltar uma palavra-chave porque a pessoa não tem essa experiência, liste em
  missing_keywords, mas NÃO escreva uma frase fingindo que tem.
- Marcadores como [EMAIL], [TELEFONE] e [URL] protegem dados pessoais. Ignore-os.
- Escreva em português, a menos que o currículo esteja em inglês: nesse caso, escreva
  as sugestões em inglês."""


def optimize_resume(resume_text: str, job_text: str) -> ResumeOptimization:
    llm = get_groq_llm().with_structured_output(ResumeOptimization)
    return llm.invoke(
        [
            ("system", SYSTEM_PROMPT),
            (
                "human",
                f"CURRÍCULO:\n{sanitize_text(resume_text)}\n\nVAGA:\n{sanitize_text(job_text)}",
            ),
        ]
    )