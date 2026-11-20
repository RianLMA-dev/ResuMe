import io

import pytest
from pypdf import PdfWriter

from app.services.pdf import (
    MAX_PAGES,
    MAX_PDF_BYTES,
    PdfExtractionError,
    clean_text,
    extract_text_from_pdf,
)


def make_pdf(lines: list[str]) -> bytes:
    """Monta um PDF mínimo, só com texto, para os testes."""
    content = "BT /F1 12 Tf 72 720 Td 16 TL\n"
    content += "\n".join(f"({line}) Tj T*" for line in lines)
    content += "\nET"
    objects = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        "/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        f"<< /Length {len(content)} >>\nstream\n{content}\nendstream",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = "%PDF-1.4\n"
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{number} 0 obj\n{body}\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n"
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n"
    out += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF"
    return out.encode("latin-1")


def blank_pdf(pages: int, password: str | None = None) -> bytes:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=200, height=200)
    if password:
        writer.encrypt(password)
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


LINES = [
    "EXPERIENCIA",
    "Analista de Dados Junior | Empresa Exemplo | 2025 - atual",
    "- Automatizei relatorios semanais com Python e Pandas",
    "- Escrevi consultas SQL em PostgreSQL",
]


def test_clean_text_preserva_quebras_de_linha():
    texto = "EXPERIENCIA\r\n\r\n\r\n\r\nAnalista   de  Dados \t Junior  \n- Python   e SQL"
    assert clean_text(texto) == "EXPERIENCIA\n\nAnalista de Dados Junior\n- Python e SQL"


def test_clean_text_vazio():
    assert clean_text("") == ""
    assert clean_text(None) == ""


def test_extrai_o_texto_mantendo_a_estrutura():
    texto = extract_text_from_pdf(make_pdf(LINES))
    assert "EXPERIENCIA\nAnalista de Dados Junior" in texto
    assert texto.count("\n") >= 3


def test_arquivo_que_nao_e_pdf():
    with pytest.raises(PdfExtractionError, match="não parece ser um PDF"):
        extract_text_from_pdf(b"isto nao e um pdf")


def test_pdf_grande_demais():
    with pytest.raises(PdfExtractionError, match="5 MB"):
        extract_text_from_pdf(b"%PDF-" + b"0" * (MAX_PDF_BYTES + 1))


def test_pdf_com_paginas_demais():
    with pytest.raises(PdfExtractionError, match="páginas"):
        extract_text_from_pdf(blank_pdf(MAX_PAGES + 1))


def test_pdf_com_senha():
    with pytest.raises(PdfExtractionError, match="senha"):
        extract_text_from_pdf(blank_pdf(1, password="segredo"))


def test_pdf_sem_texto_selecionavel():
    with pytest.raises(PdfExtractionError, match="selecionável"):
        extract_text_from_pdf(blank_pdf(1))


def test_pdf_corrompido_nao_vaza_detalhes_internos():
    with pytest.raises(PdfExtractionError) as erro:
        extract_text_from_pdf(b"%PDF-1.4\nlixo qualquer sem estrutura")
    assert str(erro.value) == "Não consegui ler esse PDF."
