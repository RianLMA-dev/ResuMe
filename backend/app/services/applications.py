from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import ApplicationRecord
from app.schemas import ApplicationStatus, JobApplication


def upsert_application(db: Session, data: JobApplication) -> ApplicationRecord:
    record = db.scalar(
        select(ApplicationRecord).where(
            func.lower(ApplicationRecord.company_name) == data.company_name.lower(),
            func.lower(ApplicationRecord.job_title) == data.job_title.lower(),
        )
    )

    if record is None:
        record = ApplicationRecord(
            company_name=data.company_name,
            job_title=data.job_title,
            status=data.status.value,
            key_requirements=data.key_requirements,
            next_steps=data.next_steps,
            confidence=data.confidence,
        )
        db.add(record)
    else:
        if data.status != ApplicationStatus.UNKNOWN:
            record.status = data.status.value
        if data.next_steps:
            record.next_steps = data.next_steps
        merged = list(dict.fromkeys(record.key_requirements + data.key_requirements))
        record.key_requirements = merged
        record.confidence = data.confidence

    db.commit()
    db.refresh(record)
    return record