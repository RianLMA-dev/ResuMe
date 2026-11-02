from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.graph import graph
from app.models import ProcessedEmail
from app.schemas import EmailInput
from app.services.applications import upsert_application
from app.services.gmail import get_message, get_service, list_message_ids

LABEL = "Vagas"
MAX_LOOKUP = 50  # quantos e-mails da gaveta olhar
BATCH_SIZE = 5  # quantos analisar por clique (cada e-mail = 2 chamadas ao Gemini)


class GmailSyncResult(BaseModel):
    checked: int
    saved: int
    discarded: int
    remaining: int
    stopped_by_error: bool = False


def sync_gmail(db: Session) -> GmailSyncResult:
    service = get_service()
    ids = list_message_ids(service, LABEL, max_results=MAX_LOOKUP)

    known = set(
        db.scalars(select(ProcessedEmail.gmail_id).where(ProcessedEmail.gmail_id.in_(ids)))
    )
    new_ids = [message_id for message_id in ids if message_id not in known]

    saved = 0
    discarded = 0
    stopped = False

    for message_id in new_ids[:BATCH_SIZE]:
        message = get_message(service, message_id)
        try:
            result = graph.invoke({"email": EmailInput(raw_text=message["text"])})
        except Exception:
            stopped = True
            break

        application_id = None
        if result.get("application"):
            record = upsert_application(db, result["application"])
            application_id = record.id
            outcome = "saved"
            saved += 1
        else:
            outcome = "discarded"
            discarded += 1

        db.add(ProcessedEmail(gmail_id=message_id, outcome=outcome, application_id=application_id))
        db.commit()

    processed = saved + discarded
    return GmailSyncResult(
        checked=processed,
        saved=saved,
        discarded=discarded,
        remaining=len(new_ids) - processed,
        stopped_by_error=stopped,
    )