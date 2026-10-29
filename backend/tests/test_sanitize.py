from app.services.sanitize import sanitize_text


def test_remove_email_e_url():
    texto = "Fale com ana@empresa.com ou acesse https://teste.com/x?token=abc123"
    resultado = sanitize_text(texto)
    assert "ana@empresa.com" not in resultado
    assert "abc123" not in resultado
    assert "[EMAIL]" in resultado and "[URL]" in resultado


def test_remove_telefone_e_cpf():
    resultado = sanitize_text("Tel: (85) 99999-1234 CPF: 123.456.789-09")
    assert "99999-1234" not in resultado
    assert "123.456.789-09" not in resultado


def test_preserva_conteudo_util():
    texto = "Olá! Sua candidatura para Engenheiro de IA na Acme foi recebida."
    assert sanitize_text(texto) == texto