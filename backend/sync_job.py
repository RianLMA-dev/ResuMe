import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app import models  # noqa: F401  (registra as tabelas)
from app.db import Base, SessionLocal, engine
from app.services.scheduled_sync import EXIT_ERROR, run_scheduled_sync

LOG_FILE = Path(__file__).resolve().parent / "logs" / "sync.log"


def setup_logging() -> None:
    LOG_FILE.parent.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            RotatingFileHandler(LOG_FILE, maxBytes=500_000, backupCount=2, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    logging.getLogger("resume.sync").setLevel(logging.INFO)


def main() -> int:
    setup_logging()
    log = logging.getLogger("resume.sync")
    log.info("Iniciando sincronização agendada")

    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        log.exception("Banco indisponível. O Docker Desktop está aberto e o contêiner db rodando?")
        return EXIT_ERROR

    with SessionLocal() as db:
        return run_scheduled_sync(db)


if __name__ == "__main__":
    sys.exit(main())