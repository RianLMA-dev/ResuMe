import io
import re
from pypdf import PdfReader
from fastapi import HTTPException

def clean_text(text: str) -> str:
    """Remove quebras de linha em excesso e múltiplos espaços fragmentados."""
    if not text:
        return ""
    # Substitui sequências de quebras de linha e espaços por um único espaço
    cleaned = re.sub(r'\s+', ' ', text)
    return cleaned.strip()

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extrai e sanitiza todo o texto contido em um arquivo PDF enviado em memória."""
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_file)
        extracted_text = []

        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text.append(text)

        raw_text = "\n".join(extracted_text).strip()

        if not raw_text:
            raise HTTPException(
                status_code=400,
                detail="Não foi possível extrair texto do PDF. O arquivo pode ser uma imagem/digitalização."
            )

        # Normaliza o texto removendo os caracteres de espaço/quebra entre letras
        return clean_text(raw_text)

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=f"Erro ao processar o arquivo PDF: {str(e)}")