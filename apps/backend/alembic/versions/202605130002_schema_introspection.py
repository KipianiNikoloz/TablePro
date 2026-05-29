"""schema introspection

Revision ID: 202605130002
Revises: 202605130001
Create Date: 2026-05-13
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "202605130002"
down_revision = "202605130001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "schema_snapshots",
        sa.Column("connection_id", sa.String(length=64), primary_key=True),
        sa.Column("dialect", sa.String(length=20), nullable=False),
        sa.Column("snapshot_json", sa.Text(), nullable=False),
        sa.Column("refreshed_at", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.String(length=40), nullable=False),
        sa.Column("updated_at", sa.String(length=40), nullable=False),
        sa.ForeignKeyConstraint(
            ["connection_id"],
            ["database_connections.id"],
            name="fk_schema_snapshots_connection",
        ),
    )
    op.create_index("ix_schema_snapshots_dialect", "schema_snapshots", ["dialect"])


def downgrade() -> None:
    op.drop_index("ix_schema_snapshots_dialect", table_name="schema_snapshots")
    op.drop_table("schema_snapshots")
