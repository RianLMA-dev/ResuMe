from app.schemas import ApplicationStatus, JobApplication
from app.services.gmail import GmailAuthError

FAKE_MESSAGES = {
    "m1": {
        "id": "m1",
        "subject": "Retorno",
        "text": "Assunto: Retorno\n\nSua candidatura na Acme foi recebida.",
    },
    "m2": {
        "id": "m2",
        "subject": "Newsletter",
        "text": "Assunto: Newsletter\n\nDicas de carreira para devs.",
    },
}


class FakeGraph:
    def invoke(self, state):
        if "Acme" in state["email"].raw_text:
            return {
                "is_job_related": True,
                "reason": "vaga",
                "application": JobApplication(
                    company_name="Acme Tech",
                    job_title="Engenheiro de IA",
                    status=ApplicationStatus.APPLIED,
                    key_requirements=["Python"],
                    confidence=0.9,
                ),
            }
        return {"is_job_related": False, "reason": "newsletter"}


def mock_gmail(monkeypatch):
    monkeypatch.setattr("app.services.gmail_sync.get_service", lambda: object())
    monkeypatch.setattr(
        "app.services.gmail_sync.list_message_ids",
        lambda service, label, max_results: list(FAKE_MESSAGES),
    )
    monkeypatch.setattr(
        "app.services.gmail_sync.get_message",
        lambda service, message_id: FAKE_MESSAGES[message_id],
    )
    monkeypatch.setattr("app.services.gmail_sync.graph", FakeGraph())


def test_sync_salva_a_vaga_e_descarta_o_resto(client, monkeypatch):
    mock_gmail(monkeypatch)

    response = client.post("/gmail/sync")

    assert response.status_code == 200
    body = response.json()
    assert body["checked"] == 2
    assert body["saved"] == 1
    assert body["discarded"] == 1
    assert body["remaining"] == 0
    assert len(client.get("/applications").json()) == 1


def test_sync_nao_analisa_o_mesmo_email_duas_vezes(client, monkeypatch):
    mock_gmail(monkeypatch)
    client.post("/gmail/sync")

    second = client.post("/gmail/sync").json()

    assert second["checked"] == 0
    assert len(client.get("/applications").json()) == 1


def test_sync_sem_autorizacao_retorna_401(client, monkeypatch):
    def sem_permissao():
        raise GmailAuthError("sem permissão")

    monkeypatch.setattr("app.services.gmail_sync.get_service", sem_permissao)

    assert client.post("/gmail/sync").status_code == 401