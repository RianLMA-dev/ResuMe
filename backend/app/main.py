from fastapi import FastAPI

from app.api.emails import router as emails_router

app = FastAPI(title="ResuMe")
app.include_router(emails_router)


@app.get("/health")
def health():
    return {"status": "ok"}