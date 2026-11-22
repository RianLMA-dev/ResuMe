"""adiciona applications.company_domain

Antes do Alembic, essa coluna era criada à mão em bancos antigos. O teste de
existência deixa a migração segura em bancos que já a têm.

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-22
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column() -> bool:
    columns = sa.inspect(op.get_bind()).get_columns("applications")
    return any(column["name"] == "company_domain" for column in columns)


def upgrade() -> None:
    if not _has_column():
        op.add_column(
            "applications",
            sa.Column("company_domain", sa.String(length=200), nullable=True),
        )


def downgrade() -> None:
    if _has_column():
        with op.batch_alter_table("applications") as batch:
            batch.drop_column("company_domain")
