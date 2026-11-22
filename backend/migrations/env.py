"""Ambiente do Alembic.

Usa o mesmo banco e os mesmos modelos do app. Quando chamado por
app.migrate.run_migrations, a conexão vem pronta em config.attributes.
"""
from alembic import context

from app import models  # noqa: F401  (registra as tabelas no metadata)
from app.db import DATABASE_URL, Base, engine

config = context.config
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connection = config.attributes.get("connection")
    if connection is not None:
        _run(connection)
        return
    with engine.connect() as connection:
        _run(connection)
        connection.commit()


def _run(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
