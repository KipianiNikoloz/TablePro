"""connection management

Revision ID: 202605130001
Revises: 202605090001
Create Date: 2026-05-13
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "202605130001"
down_revision = "202605090001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "database_connections",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("dialect", sa.String(length=20), nullable=False),
        sa.Column("host", sa.String(length=255), nullable=False),
        sa.Column("port", sa.Integer(), nullable=False),
        sa.Column("database", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("environment_label", sa.String(length=40), nullable=False),
        sa.Column("password_secret_ref", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.String(length=40), nullable=False),
        sa.Column("updated_at", sa.String(length=40), nullable=False),
        sa.Column("deleted_at", sa.String(length=40), nullable=True),
        sa.CheckConstraint(
            "dialect IN ('postgres', 'mysql')",
            name="ck_database_connections_dialect",
        ),
        sa.CheckConstraint("port > 0 AND port <= 65535", name="ck_database_connections_port"),
    )
    op.create_index(
        "ix_database_connections_deleted_at",
        "database_connections",
        ["deleted_at"],
    )
    op.create_index(
        "ix_database_connections_dialect",
        "database_connections",
        ["dialect"],
    )


def downgrade() -> None:
    op.drop_index("ix_database_connections_dialect", table_name="database_connections")
    op.drop_index("ix_database_connections_deleted_at", table_name="database_connections")
    op.drop_table("database_connections")
