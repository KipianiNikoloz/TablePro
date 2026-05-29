from __future__ import annotations

from dataclasses import asdict
import json
from typing import Any

from sqlalchemy import Engine, create_engine, text

from tablepro_backend.core.config import Settings
from tablepro_backend.domain.schema import (
    SchemaColumn,
    SchemaIndex,
    SchemaRelationship,
    SchemaSnapshot,
    SchemaSnapshotNotFoundError,
    SchemaTable,
)
from tablepro_backend.infrastructure.database.vault import from_db_time, to_db_time, utc_now


class SQLiteSchemaRepository:
    def __init__(self, settings: Settings, engine: Engine | None = None) -> None:
        self.settings = settings
        self.engine = engine or create_engine(settings.sqlite_url)

    def get_latest(self, connection_id: str) -> SchemaSnapshot:
        with self.engine.connect() as connection:
            row = (
                connection.execute(
                    text(
                        "SELECT connection_id, dialect, snapshot_json, refreshed_at "
                        "FROM schema_snapshots WHERE connection_id = :connection_id"
                    ),
                    {"connection_id": connection_id},
                )
                .mappings()
                .first()
            )
        if row is None:
            raise SchemaSnapshotNotFoundError("Schema snapshot has not been refreshed yet.")
        return self._from_row(row)

    def save(self, snapshot: SchemaSnapshot) -> SchemaSnapshot:
        now = to_db_time(utc_now())
        snapshot_json = json.dumps(
            {
                "tables": [asdict(table) for table in snapshot.tables],
            },
            separators=(",", ":"),
        )
        refreshed_at = to_db_time(snapshot.refreshed_at)
        with self.engine.begin() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM schema_snapshots WHERE connection_id = :connection_id"),
                {"connection_id": snapshot.connection_id},
            ).first()
            if exists:
                connection.execute(
                    text(
                        "UPDATE schema_snapshots SET dialect = :dialect, snapshot_json = :snapshot_json, "
                        "refreshed_at = :refreshed_at, updated_at = :updated_at "
                        "WHERE connection_id = :connection_id"
                    ),
                    {
                        "connection_id": snapshot.connection_id,
                        "dialect": snapshot.dialect,
                        "snapshot_json": snapshot_json,
                        "refreshed_at": refreshed_at,
                        "updated_at": now,
                    },
                )
            else:
                connection.execute(
                    text(
                        "INSERT INTO schema_snapshots "
                        "(connection_id, dialect, snapshot_json, refreshed_at, created_at, updated_at) "
                        "VALUES (:connection_id, :dialect, :snapshot_json, :refreshed_at, "
                        ":created_at, :updated_at)"
                    ),
                    {
                        "connection_id": snapshot.connection_id,
                        "dialect": snapshot.dialect,
                        "snapshot_json": snapshot_json,
                        "refreshed_at": refreshed_at,
                        "created_at": now,
                        "updated_at": now,
                    },
                )
        return self.get_latest(snapshot.connection_id)

    def _from_row(self, row: Any) -> SchemaSnapshot:
        payload = json.loads(row["snapshot_json"])
        return SchemaSnapshot(
            connection_id=row["connection_id"],
            dialect=row["dialect"],
            refreshed_at=from_db_time(row["refreshed_at"]),
            tables=[self._table_from_dict(table) for table in payload.get("tables", [])],
        )

    def _table_from_dict(self, data: dict[str, Any]) -> SchemaTable:
        return SchemaTable(
            schema_name=data["schema_name"],
            name=data["name"],
            columns=[
                SchemaColumn(
                    name=column["name"],
                    data_type=column["data_type"],
                    nullable=column["nullable"],
                    ordinal_position=column["ordinal_position"],
                    default=column.get("default"),
                )
                for column in data.get("columns", [])
            ],
            primary_key=data.get("primary_key", []),
            unique_identities=data.get("unique_identities", []),
            indexes=[
                SchemaIndex(
                    name=index["name"],
                    columns=index.get("columns", []),
                    unique=index["unique"],
                )
                for index in data.get("indexes", [])
            ],
            relationships=[
                SchemaRelationship(
                    name=relationship["name"],
                    columns=relationship.get("columns", []),
                    referenced_schema=relationship["referenced_schema"],
                    referenced_table=relationship["referenced_table"],
                    referenced_columns=relationship.get("referenced_columns", []),
                )
                for relationship in data.get("relationships", [])
            ],
        )
