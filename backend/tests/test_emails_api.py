from app.agents.classifier import EmailClassification
from app.schemas import ApplicationStatus, JobApplication

EMAIL = {"raw_text": "Recebemos sua candidatura para Engenheiro de IA na Acme Tech."}


def fake_application(status=ApplicationStatus.APPLIED) -> JobApplication:
    return JobApplication(
        company_name="Acme Tech",
        job_title="Engenheiro de IA",
        status=status,
        key_requirements=["Python"],
        confidence=0.9,
    )


def mock_job_email(monkeypatch, status=ApplicationStatus.APPLIED):
    monkeypatch.setattr(
        "app.agents.graph.classify_email",
        lambda email: EmailClassification(is_job_related=True, reason="Processo seletivo"),
    )
    monkeypatch.setattr(
        "app.agents.graph.extract_application",
        lambda email: fake_application(status),
    )


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_email_de_vaga_retorna_e_salva_candidatura(client, monkeypatch):
    mock_job_email(monkeypatch)

    response = client.post("/emails", json=EMAIL)

    assert response.status_code == 200
    body = response.json()
    assert body["is_job_related"] is True
    assert body["application"]["company_name"] == "Acme Tech"
    assert body["application"]["status"] == "Inscrito"
    assert body["application"]["id"] == 1
    assert len(client.get("/applications").json()) == 1


def test_mesmo_processo_atualiza_status_sem_duplicar(client, monkeypatch):
    mock_job_email(monkeypatch, ApplicationStatus.APPLIED)
    client.post("/emails", json=EMAIL)

    mock_job_email(monkeypatch, ApplicationStatus.INTERVIEW)
    client.post("/emails", json=EMAIL)

    applications = client.get("/applications").json()
    assert len(applications) == 1
    assert applications[0]["status"] == "Entrevista"


def test_spam_e_descartado_sem_extracao(client, monkeypatch):
    monkeypatch.setattr(
        "app.agents.graph.classify_email",
        lambda email: EmailClassification(is_job_related=False, reason="Propaganda"),
    )

    def nao_deveria_chamar(email):
        raise AssertionError("O extractor não deve rodar para e-mails descartados")

    monkeypatch.setattr("app.agents.graph.extract_application", nao_deveria_chamar)

    response = client.post("/emails", json=EMAIL)

    assert response.status_code == 200
    assert response.json()["application"] is None
    assert client.get("/applications").json() == []


def test_texto_curto_demais_retorna_422(client):
    response = client.post("/emails", json={"raw_text": "oi"})
    assert response.status_code == 422