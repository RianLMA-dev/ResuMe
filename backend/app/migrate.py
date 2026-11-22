"""Aplica as migrações do banco (Alembic) na subida do app e do job agendado."""
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect
from sqlalchemy.engine import Engine

from app.db import engine as default_engine

BASELINE = "0001"
_BACKEND_DIR = Path(__file__).resolve().parent.parent


def _config() -> Config:
    config = Config(str(_BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(_BACKEND_DIR / "migrations"))
    return config


def run_migrations(engine: Engine | None = None) -> None:
    """Leva o banco à última versão.

    Bancos criados antes do Alembic (pelo antigo create_all) já têm as tabelas,
    mas não a tabela alembic_version. Para eles, marcamos a versão inicial como
    aplicada e deixamos o upgrade cuidar do que faltar.
    """
    engine = engine or default_engine
    config = _config()
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        tables = set(inspect(connection).get_table_names())
        if "alembic_version" not in tables and "applications" in tables:
            command.stamp(config, BASELINE)
        command.upgrade(config, "head")
