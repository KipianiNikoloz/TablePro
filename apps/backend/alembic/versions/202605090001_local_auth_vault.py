"""local auth and vault

Revision ID: 202605090001
Revises: 202605010001
Create Date: 2026-05-09
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "202605090001"
down_revision = "202605010001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vault_state",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("kdf_algorithm", sa.String(length=80), nullable=False),
        sa.Column("kdf_iterations", sa.Integer(), nullable=False),
        sa.Column("salt", sa.LargeBinary(), nullable=False),
        sa.Column("verifier_ciphertext", sa.Text(), nullable=False),
        sa.Column("created_at", sa.String(length=40), nullable=False),
        sa.Column("updated_at", sa.String(length=40), nullable=False),
        sa.CheckConstraint("id = 1", name="ck_vault_state_singleton"),
    )

    op.create_table(
        "auth_sessions",
        sa.Column("id_hash", sa.String(length=64), primary_key=True),
        sa.Column("created_at", sa.String(length=40), nullable=False),
        sa.Column("last_seen_at", sa.String(length=40), nullable=False),
        sa.Column("expires_at", sa.String(length=40), nullable=False),
        sa.Column("revoked_at", sa.String(length=40), nullable=True),
    )
    op.create_index("ix_auth_sessions_expires_at", "auth_sessions", ["expires_at"])

    op.create_table(
        "secret_refs",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("label", sa.String(length=160), nullable=True),
        sa.Column("secret_type", sa.String(length=80), nullable=False),
        sa.Column("ciphertext", sa.Text(), nullable=False),
        sa.Column("created_at", sa.String(length=40), nullable=False),
        sa.Column("updated_at", sa.String(length=40), nullable=False),
        sa.Column("deleted_at", sa.String(length=40), nullable=True),
    )
    op.create_index("ix_secret_refs_type", "secret_refs", ["secret_type"])


def downgrade() -> None:
    op.drop_index("ix_secret_refs_type", table_name="secret_refs")
    op.drop_table("secret_refs")
    op.drop_index("ix_auth_sessions_expires_at", table_name="auth_sessions")
    op.drop_table("auth_sessions")
    op.drop_table("vault_state")
