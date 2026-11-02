import base64
import html
import re
from pathlib import Path

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# backend/secrets/ (fora do Git)
SECRETS_DIR = Path(__file__).resolve().parents[2] / "secrets"
CREDENTIALS_FILE = SECRETS_DIR / "credentials.json"
TOKEN_FILE = SECRETS_DIR / "token.json"

MAX_BODY_CHARS = 6000


class GmailAuthError(Exception):
    """O ResuMe ainda não tem permissão válida para ler o Gmail."""


def _load_token() -> Credentials | None:
    if not TOKEN_FILE.exists():
        return None

    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if creds.valid:
        return creds

    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except RefreshError:
            return None
        TOKEN_FILE.write_text(creds.to_json())
        return creds

    return None


def authorize() -> Credentials:
   
    creds = _load_token()
    if creds:
        return creds

    if not CREDENTIALS_FILE.exists():
        raise GmailAuthError(f"Arquivo não encontrado: {CREDENTIALS_FILE}")

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
    creds = flow.run_local_server(port=0)
    TOKEN_FILE.write_text(creds.to_json())
    return creds


def get_service():
#Cliente do Gmail usando a permissão já guardada (não abre o navegador)
    creds = _load_token()
    if creds is None:
        raise GmailAuthError(
            "Autorização do Gmail ausente ou expirada. Rode 'python try_gmail.py' para autorizar de novo."
        )
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def find_label_id(service, label_name: str) -> str:
    labels = service.users().labels().list(userId="me").execute().get("labels", [])
    for label in labels:
        if label["name"].lower() == label_name.lower():
            return label["id"]
    raise ValueError(f"Rótulo '{label_name}' não encontrado no Gmail")


def list_message_ids(service, label_name: str = "Vagas", max_results: int = 20) -> list[str]:
    label_id = find_label_id(service, label_name)
    response = (
        service.users()
        .messages()
        .list(userId="me", labelIds=[label_id], maxResults=max_results)
        .execute()
    )
    return [message["id"] for message in response.get("messages", [])]


def _header(headers: list[dict], name: str) -> str:
    for header in headers:
        if header["name"].lower() == name.lower():
            return header["value"]
    return ""


def _decode(data: str) -> str:
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded).decode("utf-8", errors="replace")


def _find_part(payload: dict, mime_type: str) -> str | None:
#Procura, dentro do e-mail, a parte com o tipo pedido (texto puro ou HTML).
    if payload.get("mimeType") == mime_type and payload.get("body", {}).get("data"):
        return _decode(payload["body"]["data"])
    for part in payload.get("parts", []) or []:
        found = _find_part(part, mime_type)
        if found:
            return found
    return None


def _html_to_text(raw: str) -> str:
    raw = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(raw)).strip()


def get_message(service, message_id: str) -> dict:
    """Devolve o assunto e o texto do e-mail, prontos para o fluxo da IA."""
    message = service.users().messages().get(userId="me", id=message_id, format="full").execute()
    payload = message["payload"]

    subject = _header(payload.get("headers", []), "Subject")

    body = _find_part(payload, "text/plain")
    if not body:
        html_body = _find_part(payload, "text/html")
        body = _html_to_text(html_body) if html_body else message.get("snippet", "")
    body = re.sub(r"\n{3,}", "\n\n", body).strip()

    return {
        "id": message_id,
        "subject": subject,
        "text": f"Assunto: {subject}\n\n{body[:MAX_BODY_CHARS]}",
    }