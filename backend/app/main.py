import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401  (registra as tabelas)
from app.api.applications import router as applications_router
from app.api.emails import router as emails_router
from app.db import Base, engine

load_dotenv()

origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # MVP: cria as tabelas se não existirem
    yield


app = FastAPI(title="ResuMe", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(emails_router)
app.include_router(applications_router)


@app.get("/health")
def health():
    return {"status": "ok"}