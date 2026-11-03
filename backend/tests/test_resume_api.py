from app.schemas import ResumeOptimization

RESUME = {
    "content": "Desenvolvedor Python com experiência em FastAPI, SQL e projetos de IA. " * 2
}
JOB_SEEN = []


def fake_optimize(resume_text, job_text):
    JOB_SEEN.append(job_text)
    return ResumeOptimization(
        matching_score=70,
        missing_keywords=["Docker"],
        suggested_bullet_points=["Destaque seu uso de FastAPI."],
    )


def mock_optimizer(monkeypatch):
    JOB_SEEN.clear()
    monkeypatch.setattr("app.api.resume.optimize_resume", fake_optimize)


def test_salva_e_le_o_curriculo(client):
    assert client.put("/resume", json=RESUME).status_code == 200

    response = client.get("/resume")

    assert response.status_code == 200
    assert response.json()["content"] == RESUME["content"]


def test_ler_sem_curriculo_retorna_404(client):
    assert client.get("/resume").status_code == 404


def test_otimizar_sem_curriculo_retorna_409(client, monkeypatch):
    mock_optimizer(monkeypatch)

    response = client.post("/optimize", json={"job_description": "Vaga de Python"})

    assert response.status_code == 409
    assert JOB_SEEN == []


def test_otimizar_com_descricao_colada(client, monkeypatch):
    mock_optimizer(monkeypatch)
    client.put("/resume", json=RESUME)

    response = client.post("/optimize", json={"job_description": "Vaga de Python com Docker"})

    assert response.status_code == 200
    body = response.json()
    assert body["matching_score"] == 70
    assert body["missing_keywords"] == ["Docker"]
    assert JOB_SEEN == ["Vaga de Python com Docker"]


def test_otimizar_com_candidatura_usa_os_dados_do_cartao(client, monkeypatch):
    mock_optimizer(monkeypatch)
    client.put("/resume", json=RESUME)
    created = client.post(
        "/applications",
        json={
            "company_name": "Globex",
            "job_title": "Engenheiro de Dados",
            "key_requirements": ["SQL"],
        },
    ).json()

    response = client.post("/optimize", json={"application_id": created["id"]})

    assert response.status_code == 200
    assert "Globex" in JOB_SEEN[0]
    assert "SQL" in JOB_SEEN[0]


def test_otimizar_sem_vaga_retorna_422(client):
    assert client.post("/optimize", json={}).status_code == 422


def test_otimizar_candidatura_inexistente_retorna_404(client, monkeypatch):
    mock_optimizer(monkeypatch)
    client.put("/resume", json=RESUME)

    assert client.post("/optimize", json={"application_id": 999}).status_code == 404