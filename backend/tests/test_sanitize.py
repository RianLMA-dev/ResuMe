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


def test_numero_de_vaga_nao_vira_telefone():
    for texto in (
        "Autoglass 11323783 - Cientista de Dados I",
        "vaga 12411574 - ESTAGIARIO DE TECNOLOGIA",
        "Candidatura 20458817 recebida",
    ):
        assert sanitize_text(texto) == texto


def test_formatos_comuns_de_telefone_continuam_removidos():
    for telefone in (
        "(85) 99999-1234",
        "+55 85 99999-1234",
        "85 3333-4444",
        "85-98802-0681",
        "85-988020681",
        "9999-8888",
        "11999998888",
    ):
        resultado = sanitize_text(f"Ligue para {telefone} hoje")
        # 11 dígitos sem formatação têm o mesmo formato de um CPF, que é filtrado antes.
        assert "[TELEFONE]" in resultado or "[CPF]" in resultado, telefone
        assert telefone not in resultado, telefone


def test_anos_e_datas_nao_viram_telefone():
    for texto in ("Programa de Estágio 2025-2026", "Prazo: 2026-11-20", "Inscrições até 20/11/2026"):
        assert sanitize_text(texto) == texto

