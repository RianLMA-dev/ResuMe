"""baseline: tabelas iniciais

Estado do banco antes do campo company_domain. Bancos criados pelo antigo
create_all já têm estas tabelas; para eles, app.migrate marca esta versão
como aplicada (stamp) em vez de recriá-las.

Revision ID: 0001
Revises:
Create Date: 2026-11-22
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_name", sa.String(length=200), nullable=False),
        sa.Column("job_title", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("key_requirements", sa.JSON(), nullable=False),
        sa.Column("next_steps", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_applications_company_name", "applications", ["company_name"])
    op.create_index("ix_applications_job_title", "applications", ["job_title"])

    op.create_table(
        "base_resume",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "processed_emails",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("gmail_id", sa.String(length=64), nullable=False),
        sa.Column("outcome", sa.String(length=20), nullable=False),
        sa.Column("application_id", sa.Integer(), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_processed_emails_gmail_id", "processed_emails", ["gmail_id"], unique=True
    )


def downgrade() -> None:
    op.drop_index("ix_processed_emails_gmail_id", table_name="processed_emails")
    op.drop_table("processed_emails")
    op.drop_table("base_resume")
    op.drop_index("ix_applications_job_title", table_name="applications")
    op.drop_index("ix_applications_company_name", table_name="applications")
    op.drop_table("applications")
