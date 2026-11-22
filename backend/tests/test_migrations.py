import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.db import Base
from app.migrate import run_migrations


@pytest.fixture
def engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _version(engine) -> str:
    with engine.connect() as conn:
        return conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one()


def _columns(engine, table: str) -> set[str]:
    return {c["name"] for c in inspect(engine).get_columns(table)}


def test_banco_novo_fica_igual_aos_modelos(engine):
    run_migrations(engine)

    with engine.connect() as conn:
        diff = compare_metadata(MigrationContext.configure(conn), Base.metadata)
    assert diff == [], f"modelos e migrações divergem: {diff}"
    assert _version(engine) == "0003"


def test_rodar_duas_vezes_nao_quebra(engine):
    run_migrations(engine)
    run_migrations(engine)
    assert _version(engine) == "0003"


def test_banco_antigo_do_create_all_e_adotado_sem_perder_dados(engine):
    Base.metadata.create_all(engine)
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO applications (company_name, job_title, status, "
                "key_requirements, confidence, created_at, updated_at) "
                "VALUES ('Acme', 'Dev', 'Inscrito', '[]', 0.9, "
                "'2026-01-01 00:00:00', '2026-01-01 00:00:00')"
            )
        )

    run_migrations(engine)

    assert _version(engine) == "0003"
    with engine.connect() as conn:
        assert conn.execute(text("SELECT company_name FROM applications")).scalar_one() == "Acme"


def test_banco_antigo_sem_company_domain_ganha_a_coluna(engine):
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE applications (id INTEGER PRIMARY KEY, company_name VARCHAR(200) NOT NULL, "
                "job_title VARCHAR(200) NOT NULL, status VARCHAR(50) NOT NULL, key_requirements JSON NOT NULL, "
                "next_steps TEXT, confidence FLOAT NOT NULL, created_at DATETIME NOT NULL, updated_at DATETIME NOT NULL)"
            )
        )
        conn.execute(
            text(
                "INSERT INTO applications VALUES (1, 'Acme', 'Dev', 'Inscrito', '[]', NULL, 0.9, "
                "'2026-01-01 00:00:00', '2026-01-01 00:00:00')"
            )
        )
        conn.execute(
            text(
                "CREATE TABLE base_resume (id INTEGER PRIMARY KEY, content TEXT NOT NULL, "
                "updated_at DATETIME NOT NULL)"
            )
        )
        conn.execute(
            text(
                "CREATE TABLE processed_emails (id INTEGER PRIMARY KEY, gmail_id VARCHAR(64) NOT NULL, "
                "outcome VARCHAR(20) NOT NULL, application_id INTEGER, processed_at DATETIME NOT NULL)"
            )
        )

    run_migrations(engine)

    assert "company_domain" in _columns(engine, "applications")
    with engine.connect() as conn:
        assert conn.execute(text("SELECT company_name FROM applications")).scalar_one() == "Acme"


def test_descer_e_subir_de_novo_nao_perde_o_esquema(engine):
    from alembic import command

    from app.migrate import _config

    run_migrations(engine)
    config = _config()
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.downgrade(config, "0002")

    assert "session_id" not in _columns(engine, "applications")
    assert "demo_sessions" not in inspect(engine).get_table_names()

    run_migrations(engine)

    assert _version(engine) == "0003"
    assert "session_id" in _columns(engine, "applications")
    assert "demo_sessions" in inspect(engine).get_table_names()
