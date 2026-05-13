from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from sqlalchemy import Engine, create_engine, text

from tablepro_backend.core.config import Settings
from tablepro_backend.domain.connections import (
    ConnectionInput,
    ConnectionNotFoundError,
    ConnectionUpdate,
    SavedConnection,
)
from tablepro_backend.infrastructure.database.vault import from_db_time, to_db_time, utc_now


@dataclass(frozen=True)
class ConnectionSecretRefs:
    current: str
    previous: str | None = None


class SQLiteConnectionRepository:
    def __init__(self, settings: Settings, engine: Engine | None = None) -> None:
        self.settings = settings
        self.engine = engine or create_engine(settings.sqlite_url)

    def create(self, data: ConnectionInput, password_secret_ref: str) -> SavedConnection:
        connection_id = f"conn_{uuid4().hex}"
        now = to_db_time(utc_now())
        with self.engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO database_connections "
                    "(id, name, dialect, host, port, database, username, environment_label, "
                    "password_secret_ref, created_at, updated_at, deleted_at) "
                    "VALUES (:id, :name, :dialect, :host, :port, :database, :username, "
                    ":environment_label, :password_secret_ref, :created_at, :updated_at, NULL)"
                ),
                {
                    "id": connection_id,
                    "name": data.name,
                    "dialect": data.dialect,
                    "host": data.host,
                    "port": data.port,
                    "database": data.database,
                    "username": data.username,
                    "environment_label": data.environment_label,
                    "password_secret_ref": password_secret_ref,
                    "created_at": now,
                    "updated_at": now,
                },
            )
        return self.get(connection_id)

    def list(self) -> list[SavedConnection]:
        with self.engine.connect() as connection:
            rows = (
                connection.execute(
                    text(
                        "SELECT id, name, dialect, host, port, database, username, environment_label, "
                        "password_secret_ref, created_at, updated_at "
                        "FROM database_connections WHERE deleted_at IS NULL ORDER BY name ASC, id ASC"
                    )
                )
                .mappings()
                .all()
            )
        return [self._from_row(row) for row in rows]

    def get(self, connection_id: str) -> SavedConnection:
        with self.engine.connect() as connection:
            row = (
                connection.execute(
                    text(
                        "SELECT id, name, dialect, host, port, database, username, environment_label, "
                        "password_secret_ref, created_at, updated_at "
                        "FROM database_connections WHERE id = :id AND deleted_at IS NULL"
                    ),
                    {"id": connection_id},
                )
                .mappings()
                .first()
            )
        if row is None:
            raise ConnectionNotFoundError("Connection was not found.")
        return self._from_row(row)

    def update(
        self,
        connection_id: str,
        update: ConnectionUpdate,
        *,
        password_secret_ref: str | None = None,
    ) -> ConnectionSecretRefs:
        current = self.get(connection_id)
        fields: dict[str, object] = {
            "name": update.name if update.name is not None else current.name,
            "host": update.host if update.host is not None else current.host,
            "port": update.port if update.port is not None else current.port,
            "database": update.database if update.database is not None else current.database,
            "username": update.username if update.username is not None else current.username,
            "environment_label": (
                update.environment_label
                if update.environment_label is not None
                else current.environment_label
            ),
            "password_secret_ref": password_secret_ref or current.password_secret_ref,
            "updated_at": to_db_time(utc_now()),
            "id": connection_id,
        }
        with self.engine.begin() as connection:
            result = connection.execute(
                text(
                    "UPDATE database_connections SET "
                    "name = :name, host = :host, port = :port, database = :database, "
                    "username = :username, environment_label = :environment_label, "
                    "password_secret_ref = :password_secret_ref, updated_at = :updated_at "
                    "WHERE id = :id AND deleted_at IS NULL"
                ),
                fields,
            )
        if result.rowcount != 1:
            raise ConnectionNotFoundError("Connection was not found.")
        return ConnectionSecretRefs(
            current=str(fields["password_secret_ref"]),
            previous=current.password_secret_ref if password_secret_ref else None,
        )

    def delete(self, connection_id: str) -> str:
        current = self.get(connection_id)
        with self.engine.begin() as connection:
            result = connection.execute(
                text(
                    "UPDATE database_connections SET deleted_at = :deleted_at "
                    "WHERE id = :id AND deleted_at IS NULL"
                ),
                {"deleted_at": to_db_time(utc_now()), "id": connection_id},
            )
        if result.rowcount != 1:
            raise ConnectionNotFoundError("Connection was not found.")
        return current.password_secret_ref

    def _from_row(self, row: object) -> SavedConnection:
        return SavedConnection(
            id=row["id"],
            name=row["name"],
            dialect=row["dialect"],
            host=row["host"],
            port=row["port"],
            database=row["database"],
            username=row["username"],
            environment_label=row["environment_label"],
            password_secret_ref=row["password_secret_ref"],
            created_at=from_db_time(row["created_at"]),
            updated_at=from_db_time(row["updated_at"]),
        )
