"""demonstração pública: session_id nos dados e tabelas de sessão e uso

Para o uso normal nada muda: session_id fica NULL.

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-22
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _inspector():
    return sa.inspect(op.get_bind())


def upgrade() -> None:
    # Cada passo confere antes: bancos criados pelo create_all dos modelos novos já têm tudo.
    for table in ("applications", "base_resume"):
        columns = {c["name"] for c in _inspector().get_columns(table)}
        if "session_id" not in columns:
            op.add_column(table, sa.Column("session_id", sa.String(length=64), nullable=True))
        index_name = f"ix_{table}_session_id"
        if index_name not in {i["name"] for i in _inspector().get_indexes(table)}:
            op.create_index(index_name, table, ["session_id"])

    tables = set(_inspector().get_table_names())
    if "demo_sessions" not in tables:
        op.create_table(
            "demo_sessions",
            sa.Column("session_id", sa.String(length=64), primary_key=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        )
    if "demo_usage" not in tables:
        op.create_table(
            "demo_usage",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("scope", sa.String(length=16), nullable=False),
            sa.Column("key", sa.String(length=64), nullable=False),
            sa.Column("window", sa.String(length=16), nullable=False),
            sa.Column("count", sa.Integer(), nullable=False),
            sa.UniqueConstraint("scope", "key", "window", name="uq_demo_usage"),
        )


def downgrade() -> None:
    op.drop_table("demo_usage")
    op.drop_table("demo_sessions")
    for table in ("base_resume", "applications"):
        op.drop_index(f"ix_{table}_session_id", table_name=table)
        with op.batch_alter_table(table) as batch:
            batch.drop_column("session_id")
