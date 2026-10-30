from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import ApplicationRecord
from app.schemas import ApplicationRead

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("", response_model=List[ApplicationRead])
def list_applications(db: Session = Depends(get_db)):
    stmt = select(ApplicationRecord).order_by(ApplicationRecord.updated_at.desc())
    return db.scalars(stmt).all()