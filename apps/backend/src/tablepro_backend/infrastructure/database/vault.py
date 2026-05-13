from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import hashlib
import secrets
from uuid import uuid4

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from tablepro_backend.core.config import Settings
from tablepro_backend.domain.auth import SecretRefNotFoundError


def utc_now() -> datetime:
    return datetime.now(UTC)


def to_db_time(value: datetime) -> str:
    return value.astimezone(UTC).isoformat()


def from_db_time(value: str) -> datetime:
    return datetime.fromisoformat(value).astimezone(UTC)


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class VaultStateRecord:
    kdf_algorithm: str
    kdf_iterations: int
    salt: bytes
    verifier_ciphertext: str


@dataclass(frozen=True)
class SessionValidation:
    token: str
    token_hash: str


@dataclass(frozen=True)
class SecretRefRecord:
    id: str
    ciphertext: str
    label: str | None
    secret_type: str


class SQLiteVaultRepository:
    def __init__(self, settings: Settings, engine: Engine | None = None) -> None:
        self.settings = settings
        self.engine = engine or create_engine(settings.sqlite_url)

    def vault_state_exists(self) -> bool:
        try:
            with self.engine.connect() as connection:
                row = connection.execute(text("SELECT 1 FROM vault_state WHERE id = 1")).first()
        except SQLAlchemyError:
            return False
        return row is not None

    def load_vault_state(self) -> VaultStateRecord | None:
        with self.engine.connect() as connection:
            row = connection.execute(
                text(
                    "SELECT kdf_algorithm, kdf_iterations, salt, verifier_ciphertext "
                    "FROM vault_state WHERE id = 1"
                )
            ).mappings().first()
        if row is None:
            return None
        return VaultStateRecord(
            kdf_algorithm=row["kdf_algorithm"],
            kdf_iterations=row["kdf_iterations"],
            salt=bytes(row["salt"]),
            verifier_ciphertext=row["verifier_ciphertext"],
        )

    def initialize_vault(
        self,
        *,
        kdf_algorithm: str,
        kdf_iterations: int,
        salt: bytes,
        verifier_ciphertext: str,
    ) -> None:
        now = to_db_time(utc_now())
        with self.engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO vault_state "
                    "(id, kdf_algorithm, kdf_iterations, salt, verifier_ciphertext, created_at, updated_at) "
                    "VALUES (1, :algorithm, :iterations, :salt, :verifier, :created_at, :updated_at)"
                ),
                {
                    "algorithm": kdf_algorithm,
                    "iterations": kdf_iterations,
                    "salt": salt,
                    "verifier": verifier_ciphertext,
                    "created_at": now,
                    "updated_at": now,
                },
            )

    def create_session(self, idle_timeout_seconds: int) -> str:
        token = secrets.token_urlsafe(32)
        now = utc_now()
        expires_at = now + timedelta(seconds=idle_timeout_seconds)
        with self.engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO auth_sessions "
                    "(id_hash, created_at, last_seen_at, expires_at, revoked_at) "
                    "VALUES (:id_hash, :created_at, :last_seen_at, :expires_at, NULL)"
                ),
                {
                    "id_hash": hash_session_token(token),
                    "created_at": to_db_time(now),
                    "last_seen_at": to_db_time(now),
                    "expires_at": to_db_time(expires_at),
                },
            )
        return token

    def validate_session(self, token: str, idle_timeout_seconds: int) -> SessionValidation | None:
        token_hash = hash_session_token(token)
        now = utc_now()
        with self.engine.begin() as connection:
            row = connection.execute(
                text(
                    "SELECT expires_at, revoked_at FROM auth_sessions "
                    "WHERE id_hash = :id_hash"
                ),
                {"id_hash": token_hash},
            ).mappings().first()
            if row is None or row["revoked_at"] is not None:
                return None
            if from_db_time(row["expires_at"]) <= now:
                connection.execute(
                    text("UPDATE auth_sessions SET revoked_at = :revoked_at WHERE id_hash = :id_hash"),
                    {"revoked_at": to_db_time(now), "id_hash": token_hash},
                )
                return None
            connection.execute(
                text(
                    "UPDATE auth_sessions "
                    "SET last_seen_at = :last_seen_at, expires_at = :expires_at "
                    "WHERE id_hash = :id_hash"
                ),
                {
                    "last_seen_at": to_db_time(now),
                    "expires_at": to_db_time(now + timedelta(seconds=idle_timeout_seconds)),
                    "id_hash": token_hash,
                },
            )
        return SessionValidation(token=token, token_hash=token_hash)

    def revoke_session(self, token: str) -> None:
        token_hash = hash_session_token(token)
        with self.engine.begin() as connection:
            connection.execute(
                text(
                    "UPDATE auth_sessions SET revoked_at = :revoked_at "
                    "WHERE id_hash = :id_hash AND revoked_at IS NULL"
                ),
                {"revoked_at": to_db_time(utc_now()), "id_hash": token_hash},
            )

    def revoke_all_sessions(self) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                text("UPDATE auth_sessions SET revoked_at = :revoked_at WHERE revoked_at IS NULL"),
                {"revoked_at": to_db_time(utc_now())},
            )

    def create_secret_ref(
        self,
        *,
        ciphertext: str,
        label: str | None,
        secret_type: str,
    ) -> SecretRefRecord:
        ref_id = f"sec_{uuid4().hex}"
        now = to_db_time(utc_now())
        with self.engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO secret_refs "
                    "(id, label, secret_type, ciphertext, created_at, updated_at, deleted_at) "
                    "VALUES (:id, :label, :secret_type, :ciphertext, :created_at, :updated_at, NULL)"
                ),
                {
                    "id": ref_id,
                    "label": label,
                    "secret_type": secret_type,
                    "ciphertext": ciphertext,
                    "created_at": now,
                    "updated_at": now,
                },
            )
        return SecretRefRecord(id=ref_id, ciphertext=ciphertext, label=label, secret_type=secret_type)

    def load_secret_ref(self, ref_id: str) -> SecretRefRecord:
        with self.engine.connect() as connection:
            row = connection.execute(
                text(
                    "SELECT id, ciphertext, label, secret_type FROM secret_refs "
                    "WHERE id = :id AND deleted_at IS NULL"
                ),
                {"id": ref_id},
            ).mappings().first()
        if row is None:
            raise SecretRefNotFoundError("Secret reference was not found.")
        return SecretRefRecord(
            id=row["id"],
            ciphertext=row["ciphertext"],
            label=row["label"],
            secret_type=row["secret_type"],
        )

    def update_secret_ref(self, ref_id: str, ciphertext: str) -> None:
        with self.engine.begin() as connection:
            result = connection.execute(
                text(
                    "UPDATE secret_refs SET ciphertext = :ciphertext, updated_at = :updated_at "
                    "WHERE id = :id AND deleted_at IS NULL"
                ),
                {"id": ref_id, "ciphertext": ciphertext, "updated_at": to_db_time(utc_now())},
            )
        if result.rowcount != 1:
            raise SecretRefNotFoundError("Secret reference was not found.")

    def delete_secret_ref(self, ref_id: str) -> None:
        with self.engine.begin() as connection:
            result = connection.execute(
                text(
                    "UPDATE secret_refs SET deleted_at = :deleted_at "
                    "WHERE id = :id AND deleted_at IS NULL"
                ),
                {"id": ref_id, "deleted_at": to_db_time(utc_now())},
            )
        if result.rowcount != 1:
            raise SecretRefNotFoundError("Secret reference was not found.")
