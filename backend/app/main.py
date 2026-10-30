from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401  (registra as tabelas)
from app.api.applications import router as applications_router
from app.api.emails import router as emails_router
from app.db import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # MVP: cria as tabelas se não existirem
    yield


app = FastAPI(title="ResuMe", lifespan=lifespan)
app.include_router(emails_router)
app.include_router(applications_router)


@app.get("/health")
def health():
    return {"status": "ok"}