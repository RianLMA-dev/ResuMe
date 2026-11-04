# fix_db.py
from app.db import engine
from sqlalchemy import text

def add_column():
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE applications ADD COLUMN IF NOT EXISTS company_domain VARCHAR(200);"))
        conn.commit()
        print("Coluna company_domain adicionada com sucesso!")

if __name__ == "__main__":
    add_column()