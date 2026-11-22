import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://resume:resume@localhost:5432/resume"
)

# SQLite é usado na demonstração pública (sem servidor de banco): as rotas rodam em threads.
_connect_args = (
    {"check_same_thread": False, "timeout": 15} if DATABASE_URL.startswith("sqlite") else {}
)
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()