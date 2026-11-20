import re

_PATTERNS = [
    ("URL", re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)),
    ("EMAIL", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")),
    ("CPF", re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")),
    (
        # Telefone brasileiro. Exige DDD (de 10 a 11 dígitos) ou, sem DDD, um hífen no meio
        # (9999-8888). Assim, números de vaga de 8 dígitos (ex.: 11323783) e anos
        # (2025-2026) não são confundidos com telefone.
        "TELEFONE",
        re.compile(
            r"(?<![\d-])(?:"
            r"(?:\+?55[\s-]?)?\(?\d{2}\)?[\s-]?9?\d{4}[\s-]?\d{4}"
            r"|(?!(?:19|20)\d{2}-(?:19|20)\d{2})9?\d{4}-\d{4}"
            r")(?!\d)"
        ),
    ),
]


def sanitize_text(text: str) -> str:
    for label, pattern in _PATTERNS:
        text = pattern.sub(f"[{label}]", text)
    return text