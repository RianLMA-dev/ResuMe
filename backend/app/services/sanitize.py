import re

_PATTERNS = [
    ("URL", re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)),
    ("EMAIL", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")),
    ("CPF", re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")),
    (
        "TELEFONE",
        re.compile(r"(?<!\d)(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?9?\s?\d{4}[-\s]?\d{4}(?!\d)"),
    ),
]


def sanitize_text(text: str) -> str:
    for label, pattern in _PATTERNS:
        text = pattern.sub(f"[{label}]", text)
    return text