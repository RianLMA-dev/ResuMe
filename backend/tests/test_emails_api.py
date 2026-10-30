from fastapi.testclient import TestClient

from app.agents.classifier import EmailClassification
from app.main import app
from app.schemas import ApplicationStatus, JobApplication

client = TestClient(app)

EMAIL = {"raw_text": "Recebemos sua candidatura para Engenheiro de IA na Acme Tech."}


def fake_application() -> JobApplication:
    return JobApplication(
        company_name="Acme Tech",
        job_title="Engenheiro de IA",
        status=ApplicationStatus.APPLIED,
        key_requirements=["Python"],
        confidence=0.9,
    )


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_email_de_vaga_retorna_candidatura(monkeypatch):
    monkeypatch.setattr(
        "app.agents.graph.classify_email",
        lambda email: EmailClassification(is_job_related=True, reason="Processo seletivo"),
    )
    monkeypatch.setattr(
        "app.agents.graph.extract_application",
        lambda email: fake_application(),
    )

    response = client.post("/emails", json=EMAIL)

    assert response.status_code == 200
    body = response.json()
    assert body["is_job_related"] is True
    assert body["application"]["company_name"] == "Acme Tech"
    assert body["application"]["status"] == "Inscrito"


def test_spam_e_descartado_sem_extracao(monkeypatch):
    monkeypatch.setattr(
        "app.agents.graph.classify_email",
        lambda email: EmailClassification(is_job_related=False, reason="Propaganda"),
    )

    def nao_deveria_chamar(email):
        raise AssertionError("O extractor não deve rodar para e-mails descartados")

    monkeypatch.setattr("app.agents.graph.extract_application", nao_deveria_chamar)

    response = client.post("/emails", json=EMAIL)

    assert response.status_code == 200
    body = response.json()
    assert body["is_job_related"] is False
    assert body["application"] is None


def test_texto_curto_demais_retorna_422():
    response = client.post("/emails", json={"raw_text": "oi"})
    assert response.status_code == 422