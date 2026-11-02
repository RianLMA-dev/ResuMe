from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.gmail import GmailAuthError
from app.services.gmail_sync import GmailSyncResult, sync_gmail

router = APIRouter(prefix="/gmail", tags=["gmail"])


@router.post("/sync", response_model=GmailSyncResult)
def sync(db: Session = Depends(get_db)):
    """Lê os e-mails novos do marcador Vagas e atualiza o kanban."""
    try:
        return sync_gmail(db)
    except GmailAuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=502, detail="Falha ao falar com o Gmail.")