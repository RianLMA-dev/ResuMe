from tests.test_pdf_service import LINES, blank_pdf, make_pdf


def _post(client, nome, conteudo):
    return client.post("/resume/upload", files={"file": (nome, conteudo, "application/pdf")})


def test_upload_salva_o_curriculo_com_quebras_de_linha(client):
    resp = _post(client, "cv.pdf", make_pdf(LINES))
    assert resp.status_code == 200
    assert "EXPERIENCIA\nAnalista de Dados Junior" in resp.json()["content"]
    assert client.get("/resume").json()["content"] == resp.json()["content"]


def test_upload_rejeita_extensao_errada(client):
    assert _post(client, "cv.txt", b"oi").status_code == 400


def test_upload_rejeita_arquivo_que_nao_e_pdf(client):
    resp = _post(client, "cv.pdf", b"isto nao e um pdf")
    assert resp.status_code == 400
    assert "PDF" in resp.json()["detail"]


def test_upload_rejeita_pdf_sem_texto(client):
    resp = _post(client, "cv.pdf", blank_pdf(1))
    assert resp.status_code == 400
    assert "selecionável" in resp.json()["detail"]


def test_upload_nao_vaza_detalhes_de_pdf_corrompido(client):
    resp = _post(client, "cv.pdf", b"%PDF-1.4\nlixo qualquer sem estrutura")
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Não consegui ler esse PDF."
