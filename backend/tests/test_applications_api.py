NEW_APPLICATION = {
    "company_name": "Globex",
    "job_title": "Engenheiro de Dados",
    "key_requirements": ["SQL", "Python"],
}

def test_cria_candidatura_manual(client):
    response = client.post("/applications", json=NEW_APPLICATION)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["status"] == "Inscrito"
    assert body["confidence"] == 1.0


def test_atualiza_status_e_mantem_o_resto(client):
    created = client.post("/applications", json=NEW_APPLICATION).json()

    response = client.patch(f"/applications/{created['id']}", json={"status": "Entrevista"})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "Entrevista"
    assert body["company_name"] == "Globex"
    assert body["key_requirements"] == ["SQL", "Python"]


def test_status_invalido_retorna_422(client):
    created = client.post("/applications", json=NEW_APPLICATION).json()

    response = client.patch(f"/applications/{created['id']}", json={"status": "Qualquer coisa"})

    assert response.status_code == 422


def test_atualizar_inexistente_retorna_404(client):
    response = client.patch("/applications/999", json={"status": "Entrevista"})
    assert response.status_code == 404


def test_apaga_candidatura(client):
    created = client.post("/applications", json=NEW_APPLICATION).json()

    response = client.delete(f"/applications/{created['id']}")

    assert response.status_code == 204
    assert client.get("/applications").json() == []


def test_apagar_inexistente_retorna_404(client):
    assert client.delete("/applications/999").status_code == 404


def test_cors_libera_o_frontend(client):
    response = client.options(
        "/applications",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"