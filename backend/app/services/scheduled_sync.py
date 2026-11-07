import logging
import time
from collections.abc import Callable

from sqlalchemy.orm import Session

from app.services.gmail import GmailAuthError
from app.services.gmail_sync import GmailSyncResult, sync_gmail

logger = logging.getLogger("resume.sync")

MAX_EMAILS_PER_RUN = 20  # teto por execução, para proteger a cota
PAUSE_BETWEEN_BATCHES = 60  # segundos entre um lote e outro
RATE_LIMIT_WAIT = 70  # segundos de espera quando a IA falha (limite por minuto)
MAX_RATE_LIMIT_RETRIES = 2

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_AUTH = 2


def run_scheduled_sync(
    db: Session,
    sync: Callable[[Session], GmailSyncResult] = sync_gmail,
    sleep: Callable[[float], None] = time.sleep,
) -> int:
    """Processa a fila do Gmail em lotes, com pausas, e devolve um código de saída."""
    analyzed = saved = discarded = remaining = 0
    retries = 0

    while analyzed < MAX_EMAILS_PER_RUN:
        try:
            result = sync(db)
        except GmailAuthError:
            logger.error("A autorização do Gmail expirou. Rode: python try_gmail.py")
            return EXIT_AUTH
        except Exception:
            logger.exception("Falha ao sincronizar o Gmail")
            return EXIT_ERROR

        analyzed += result.checked
        saved += result.saved
        discarded += result.discarded
        remaining = result.remaining

        if result.stopped_by_error:
            retries += 1
            if retries > MAX_RATE_LIMIT_RETRIES:
                logger.error(
                    "A IA continuou falhando (provável limite). Parei com %s e-mail(s) analisado(s).",
                    analyzed,
                )
                return EXIT_ERROR
            logger.warning("A IA falhou. Esperando %s s antes de tentar de novo.", RATE_LIMIT_WAIT)
            sleep(RATE_LIMIT_WAIT)
            continue

        if result.remaining == 0 or result.checked == 0:
            break

        sleep(PAUSE_BETWEEN_BATCHES)

    logger.info(
        "Sincronização concluída: %s analisado(s), %s cartão(ões), %s descartado(s), %s na fila.",
        analyzed,
        saved,
        discarded,
        remaining,
    )
    return EXIT_OK