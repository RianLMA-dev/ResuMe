import uuid
from datetime import timedelta

import pytest

from app import demo
from app.api.emails import graph as email_graph  # noqa: F401  (garante o import)
from app.db import get_db
from app.demo_seed import SAMPLE_CARDS
from app.models import ApplicationRecord, BaseResume, DemoSession
from app.models.application import utcnow
from app.schemas import ResumeOptimization
from tests.test_emails_api import EMAIL, mock_job_email


def novo_visitante() -> dict:
    return {demo.SESSION_HEADER: str(uuid.uuid4())}


@pytest.fixture
def demo_client(client, monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.setattr("app.api.emails.time.sleep", lambda _seconds: None)
    return client


def test_fora_da_demo_o_cabecalho_e_ignorado(client):
    assert client.get("/config").json()["demo"] is False
    assert client.get("/applications").json() == []
    assert client.get("/applications", headers=novo_visitante()).json() == []


def test_demo_exige_sessao_valida(demo_client):
    assert demo_client.get("/applications").status_code == 400
    assert demo_client.get("/applications", headers={demo.SESSION_HEADER: "abc"}).status_code == 400
    assert demo_client.get("/config").json()["demo"] is True


def test_visitante_novo_recebe_cartoes_e_curriculo_de_exemplo(demo_client):
    headers = novo_visitante()

    cards = demo_client.get("/applications", headers=headers).json()
    resume = demo_client.get("/resume", headers=headers)

    assert len(cards) == len(SAMPLE_CARDS)
    assert resume.status_code == 200
    assert "fictícia" in resume.json()["content"]


def test_cada_visitante_ve_so_os_proprios_dados(demo_client):
    a, b = novo_visitante(), novo_visitante()
    cards_a = demo_client.get("/applications", headers=a).json()
    demo_client.get("/applications", headers=b)

    assert demo_client.delete(f"/applications/{cards_a[0]['id']}", headers=a).status_code == 204

    assert len(demo_client.get("/applications", headers=a).json()) == len(SAMPLE_CARDS) - 1
    assert len(demo_client.get("/applications", headers=b).json()) == len(SAMPLE_CARDS)


def test_visitante_nao_mexe_no_cartao_de_outro(demo_client):
    a, b = novo_visitante(), novo_visitante()
    card_a = demo_client.get("/applications", headers=a).json()[0]
    demo_client.get("/applications", headers=b)

    assert demo_client.patch(
        f"/applications/{card_a['id']}", json={"status": "Oferta"}, headers=b
    ).status_code == 404
    assert demo_client.delete(f"/applications/{card_a['id']}", headers=b).status_code == 404


def test_apagar_tudo_nao_recria_os_exemplos(demo_client):
    headers = novo_visitante()
    for card in demo_client.get("/applications", headers=headers).json():
        demo_client.delete(f"/applications/{card['id']}", headers=headers)

    assert demo_client.get("/applications", headers=headers).json() == []


def test_curriculo_e_por_visitante(demo_client):
    a, b = novo_visitante(), novo_visitante()
    demo_client.get("/resume", headers=a)
    texto = "Currículo do visitante A. " * 5
    assert demo_client.put("/resume", json={"content": texto}, headers=a).status_code == 200

    assert demo_client.get("/resume", headers=a).json()["content"] == texto
    assert demo_client.get("/resume", headers=b).json()["content"] != texto


def test_limite_de_ia_por_sessao(demo_client, monkeypatch):
    monkeypatch.setenv("DEMO_AI_PER_SESSION_HOUR", "2")
    mock_job_email(monkeypatch)
    a = novo_visitante()

    assert demo_client.post("/emails", json=EMAIL, headers=a).status_code == 200
    assert demo_client.post("/emails", json=EMAIL, headers=a).status_code == 200
    bloqueado = demo_client.post("/emails", json=EMAIL, headers=a)

    assert bloqueado.status_code == 429
    assert "Retry-After" in bloqueado.headers
    # outro visitante continua podendo usar (o limite por rede é maior)
    assert demo_client.post("/emails", json=EMAIL, headers=novo_visitante()).status_code == 200


def test_limite_por_rede_vale_entre_sessoes(demo_client, monkeypatch):
    monkeypatch.setenv("DEMO_AI_PER_IP_HOUR", "1")
    mock_job_email(monkeypatch)

    assert demo_client.post("/emails", json=EMAIL, headers=novo_visitante()).status_code == 200
    assert demo_client.post("/emails", json=EMAIL, headers=novo_visitante()).status_code == 429


def test_limite_diario_vale_para_todos(demo_client, monkeypatch):
    monkeypatch.setenv("DEMO_AI_PER_DAY", "1")
    mock_job_email(monkeypatch)
    primeiro = {**novo_visitante(), "X-Forwarded-For": "1.1.1.1"}
    segundo = {**novo_visitante(), "X-Forwarded-For": "2.2.2.2"}

    assert demo_client.post("/emails", json=EMAIL, headers=primeiro).status_code == 200
    resposta = demo_client.post("/emails", json=EMAIL, headers=segundo)

    assert resposta.status_code == 429
    assert "hoje" in resposta.json()["detail"]


def test_gmail_fica_fora_da_demo(demo_client):
    resposta = demo_client.post("/gmail/sync", headers=novo_visitante())
    assert resposta.status_code == 403


def test_email_grande_demais_e_recusado(demo_client, monkeypatch):
    monkeypatch.setenv("DEMO_MAX_EMAIL_CHARS", "100")
    mock_job_email(monkeypatch)

    resposta = demo_client.post("/emails", json={"raw_text": "x" * 101}, headers=novo_visitante())

    assert resposta.status_code == 413


def test_limite_de_cartoes_por_visitante(demo_client, monkeypatch):
    monkeypatch.setenv("DEMO_MAX_CARDS", str(len(SAMPLE_CARDS)))
    mock_job_email(monkeypatch)
    headers = novo_visitante()

    assert demo_client.post("/emails", json=EMAIL, headers=headers).status_code == 409


def test_erro_da_ia_nao_vaza_detalhes_na_demo(demo_client, monkeypatch):
    def quebra(_state):
        raise RuntimeError("chave-secreta-do-provedor")

    monkeypatch.setattr("app.api.emails.graph.invoke", quebra)

    resposta = demo_client.post("/emails", json=EMAIL, headers=novo_visitante())

    assert resposta.status_code == 502
    assert "chave-secreta" not in resposta.text


def test_otimizar_usa_o_curriculo_e_os_cartoes_da_propria_sessao(demo_client, monkeypatch):
    monkeypatch.setattr(
        "app.api.resume.optimize_resume",
        lambda resume, job: ResumeOptimization(
            matching_score=80, missing_keywords=["Docker"], suggested_bullet_points=["x"]
        ),
    )
    a, b = novo_visitante(), novo_visitante()
    card_a = demo_client.get("/applications", headers=a).json()[0]
    demo_client.get("/applications", headers=b)

    assert demo_client.post("/optimize", json={"application_id": card_a["id"]}, headers=a).status_code == 200
    assert demo_client.post("/optimize", json={"application_id": card_a["id"]}, headers=b).status_code == 404


def test_sessoes_vencidas_somem_com_os_dados(demo_client):
    headers = novo_visitante()
    demo_client.get("/applications", headers=headers)
    db = next(demo_client.app.dependency_overrides[get_db]())

    sessao = db.query(DemoSession).one()
    sessao.created_at = utcnow() - timedelta(hours=demo.ttl_hours() + 1)
    db.commit()
    demo.purge_expired(db, force=True)

    assert db.query(DemoSession).count() == 0
    assert db.query(ApplicationRecord).count() == 0
    assert db.query(BaseResume).count() == 0
