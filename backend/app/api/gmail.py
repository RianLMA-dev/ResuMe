from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.gmail import GmailAuthError
from app.services.gmail_sync import sync_gmail

router = APIRouter(prefix="/gmail", tags=["gmail"])


def run_sync_task(db: Session):
    """Executa a sincronização capturando exceções no processo em segundo plano."""
    try:
        sync_gmail(db)
    except Exception as e:
        print(f"Erro na sincronização do Gmail em segundo plano: {e}")


@router.post("/sync")
def sync(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Inicia a sincronização dos e-mails em segundo plano e libera a requisição imediatamente."""
    background_tasks.add_task(run_sync_task, db)
    return {"status": "success", "message": "Sincronização iniciada em segundo plano."}