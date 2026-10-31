import time

from app.agents.classifier import classify_email
from app.agents.extractor import extract_application
from app.schemas import EmailInput

email = EmailInput(
    raw_text=(
        "Olá! Recebemos sua candidatura para a vaga de Analista de Dados na Initech. "
        "Seu perfil está em análise. Requisitos: SQL, Python e Power BI."
    )
)

for round_number in (1, 2):
    start = time.perf_counter()
    classify_email(email)
    classifier_time = time.perf_counter() - start

    start = time.perf_counter()
    extract_application(email)
    extractor_time = time.perf_counter() - start

    print(f"Rodada {round_number}: classifier {classifier_time:.1f}s | extractor {extractor_time:.1f}s")