from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import sqlite3

import pytest

from tablepro_backend.application.services.schema import SchemaService
from tablepro_backend.application.services.vault import VaultService
from tablepro_backend.core.config import Settings
from tablepro_backend.domain.auth import VaultLockedError
from tablepro_backend.domain.connections import ConnectionInput
from tablepro_backend.domain.schema import (
    SchemaColumn,
    SchemaIntrospectionRequest,
    SchemaRefreshError,
    SchemaSnapshot,
    SchemaSnapshotNotFoundError,
    SchemaTable,
)
from tablepro_backend.infrastructure.database.connections import SQLiteConnectionRepository
from tablepro_backend.infrastructure.database.migrations import apply_app_migrations
from tablepro_backend.infrastructure.database.schema import SQLiteSchemaRepository
from tablepro_backend.infrastructure.database.vault import SQLiteVaultRepository

PASSPHRASE = "correct horse battery staple"


class FakeSchemaIntrospector:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.requests: list[SchemaIntrospectionRequest] = []

    def introspect(self, request: SchemaIntrospectionRequest) -> SchemaSnapshot:
        self.requests.append(request)
        if self.fail:
            raise RuntimeError("boom")
        return SchemaSnapshot(
            connection_id=request.connection_id,
            dialect=request.dialect,
            refreshed_at=datetime(2026, 5, 13, tzinfo=UTC),
            tables=[
                SchemaTable(
                    schema_name="public",
                    name="users",
                    columns=[
                        SchemaColumn(
                            name="id",
                            data_type="integer",
                            nullable=False,
                            ordinal_position=1,
                        )
                    ],
                    primary_key=["id"],
                    unique_identities=[["id"]],
                )
            ],
        )


def _settings(local_tmp_path: Path) -> Settings:
    return Settings(
        data_dir=local_tmp_path,
        sqlite_path=local_tmp_path / "tablepro.sqlite3",
        vault_kdf_iterations=1000,
    )


def _connection_input(password: str = "db-password") -> ConnectionInput:
    return ConnectionInput(
        name="Local Postgres",
        dialect="postgres",
        host="localhost",
        port=5432,
        database="app",
        username="app_user",
        password=password,
        environment_label="local",
    )


def _service(
    local_tmp_path: Path,
    *,
    fail: bool = False,
) -> tuple[SchemaService, SQLiteConnectionRepository, VaultService, FakeSchemaIntrospector]:
    settings = _settings(local_tmp_path)
    apply_app_migrations(settings)
    vault_repository = SQLiteVaultRepository(settings)
    vault = VaultService(settings, vault_repository)
    vault.initialize(PASSPHRASE)
    connection_repository = SQLiteConnectionRepository(settings)
    schema_repository = SQLiteSchemaRepository(settings)
    introspector = FakeSchemaIntrospector(fail=fail)
    return (
        SchemaService(connection_repository, schema_repository, vault, introspector),
        connection_repository,
        vault,
        introspector,
    )


def test_schema_cache_miss_requires_existing_connection(local_tmp_path: Path) -> None:
    service, connection_repository, vault, _ = _service(local_tmp_path)
    saved = connection_repository.create(
        _connection_input(),
        vault.create_secret_ref("db-password"),
    )

    with pytest.raises(SchemaSnapshotNotFoundError):
        service.get_cached(saved.id)


def test_schema_refresh_stores_and_returns_snapshot(local_tmp_path: Path) -> None:
    service, connection_repository, vault, introspector = _service(local_tmp_path)
    saved = connection_repository.create(
        _connection_input("saved-password"),
        vault.create_secret_ref("saved-password"),
    )

    snapshot = service.refresh(saved.id)
    cached = service.get_cached(saved.id)

    assert snapshot == cached
    assert snapshot.tables[0].name == "users"
    assert introspector.requests[0].password == "saved-password"
    with sqlite3.connect(local_tmp_path / "tablepro.sqlite3") as connection:
        payload = connection.execute("SELECT snapshot_json FROM schema_snapshots").fetchone()[0]
    assert "saved-password" not in payload
    assert "sec_" not in payload


def test_schema_refresh_failure_preserves_previous_snapshot(local_tmp_path: Path) -> None:
    service, connection_repository, vault, introspector = _service(local_tmp_path)
    saved = connection_repository.create(
        _connection_input(),
        vault.create_secret_ref("db-password"),
    )
    first = service.refresh(saved.id)
    introspector.fail = True

    with pytest.raises(SchemaRefreshError):
        service.refresh(saved.id)

    assert service.get_cached(saved.id) == first


def test_schema_refresh_requires_unlocked_vault(local_tmp_path: Path) -> None:
    service, connection_repository, vault, _ = _service(local_tmp_path)
    saved = connection_repository.create(
        _connection_input(),
        vault.create_secret_ref("db-password"),
    )
    vault.lock()

    with pytest.raises(VaultLockedError):
        service.refresh(saved.id)
