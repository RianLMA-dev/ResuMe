import io
from pypdf import PdfReader
from fastapi import HTTPException

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extrai todo o texto contido em um arquivo PDF enviado em memória."""
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_file)
        extracted_text = []

        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text.append(text)

        full_text = "\n".join(extracted_text).strip()

        if not full_text:
            raise HTTPException(
                status_code=400,
                detail="Não foi possível extrair texto do PDF. O arquivo pode ser uma imagem/digitalização."
            )

        return full_text
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=f"Erro ao processar o arquivo PDF: {str(e)}")