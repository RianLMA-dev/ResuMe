import io
import logging
import re

from pypdf import PdfReader

logger = logging.getLogger(__name__)

MAX_PDF_BYTES = 5 * 1024 * 1024  # 5 MB
MAX_PAGES = 15
MIN_CHARS = 50
MAX_CHARS = 30000  # mesmo limite do currículo salvo (ResumeUpsert)


class PdfExtractionError(Exception):
    """O PDF não pôde ser lido. A mensagem é segura para mostrar ao usuário."""


def clean_text(text: str) -> str:
    """Limpa o texto sem apagar a estrutura: preserva as quebras de linha."""
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[^\S\n]+", " ", text)  # espaços e tabs repetidos viram um só
    text = re.sub(r" ?\n ?", "\n", text)  # tira espaços nas pontas das linhas
    text = re.sub(r"\n{3,}", "\n\n", text)  # no máximo uma linha em branco seguida
    return text.strip()


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extrai o texto de um PDF em memória. Levanta PdfExtractionError com mensagem segura."""
    if len(file_bytes) > MAX_PDF_BYTES:
        raise PdfExtractionError("O PDF passa de 5 MB.")
    if not file_bytes.lstrip().startswith(b"%PDF"):
        raise PdfExtractionError("O arquivo não parece ser um PDF.")

    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        if reader.is_encrypted:
            raise PdfExtractionError("O PDF está protegido por senha.")
        if len(reader.pages) > MAX_PAGES:
            raise PdfExtractionError(f"O PDF tem mais de {MAX_PAGES} páginas.")
        pages = [page.extract_text() or "" for page in reader.pages]
    except PdfExtractionError:
        raise
    except Exception as exc:
        # Só o tipo do erro vai para o log: o conteúdo do currículo nunca é registrado.
        logger.warning("Falha ao ler PDF: %s", type(exc).__name__)
        raise PdfExtractionError("Não consegui ler esse PDF.") from None

    text = clean_text("\n\n".join(pages))
    if len(text) < MIN_CHARS:
        raise PdfExtractionError(
            "O PDF não tem texto selecionável (pode ser uma imagem escaneada)."
        )
    if len(text) > MAX_CHARS:
        raise PdfExtractionError("O texto do PDF passa de 30.000 caracteres.")
    return text
