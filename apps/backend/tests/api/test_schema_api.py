from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from fastapi.testclient import TestClient

from tablepro_backend.application.services.schema import SchemaService
from tablepro_backend.core.config import Settings
from tablepro_backend.domain.schema import (
    SchemaColumn,
    SchemaIntrospectionRequest,
    SchemaSnapshot,
    SchemaTable,
)
from tablepro_backend.infrastructure.database.schema import SQLiteSchemaRepository
from tablepro_backend.main import create_app

PASSPHRASE = "correct horse battery staple"


class FakeSchemaIntrospector:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.requests: list[SchemaIntrospectionRequest] = []

    def introspect(self, request: SchemaIntrospectionRequest) -> SchemaSnapshot:
        self.requests.append(request)
        if self.fail:
            raise RuntimeError("refresh failed")
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
                )
            ],
        )


def _client(local_tmp_path: Path) -> tuple[TestClient, FakeSchemaIntrospector]:
    settings = Settings(
        data_dir=local_tmp_path,
        sqlite_path=local_tmp_path / "tablepro.sqlite3",
        vault_kdf_iterations=1000,
    )
    app = create_app(settings)
    introspector = FakeSchemaIntrospector()
    app.state.schema_service = SchemaService(
        app.state.connection_repository,
        SQLiteSchemaRepository(settings),
        app.state.vault_service,
        introspector,
    )
    return TestClient(app), introspector


def _connection_payload(password: str = "db-password") -> dict[str, object]:
    return {
        "name": "Local Postgres",
        "dialect": "postgres",
        "host": "localhost",
        "port": 5432,
        "database": "app",
        "username": "app_user",
        "password": password,
        "environment_label": "local",
    }


def _assert_redacted(text: str) -> None:
    lowered = text.lower()
    assert "db-password" not in lowered
    assert "secret_ref" not in lowered
    assert "ciphertext" not in lowered
    assert "sec_" not in lowered


def test_schema_api_requires_auth(local_tmp_path: Path) -> None:
    client, _ = _client(local_tmp_path)
    with client:
        response = client.get("/api/connections/conn_missing/schema")

    assert response.status_code == 401


def test_schema_cache_miss_and_refresh_success(local_tmp_path: Path) -> None:
    client, introspector = _client(local_tmp_path)
    with client:
        assert client.post("/api/auth/setup", json={"passphrase": PASSPHRASE}).status_code == 200
        create_response = client.post("/api/connections", json=_connection_payload())
        connection_id = create_response.json()["id"]
        miss_response = client.get(f"/api/connections/{connection_id}/schema")
        refresh_response = client.post(f"/api/connections/{connection_id}/schema/refresh")
        hit_response = client.get(f"/api/connections/{connection_id}/schema")

    assert miss_response.status_code == 200
    assert miss_response.json()["status"] == "missing"
    assert refresh_response.status_code == 200
    assert refresh_response.json()["snapshot"]["tables"][0]["name"] == "users"
    assert hit_response.json()["snapshot"] == refresh_response.json()["snapshot"]
    assert introspector.requests[0].password == "db-password"
    _assert_redacted(refresh_response.text + hit_response.text)


def test_schema_api_missing_connection_and_locked_vault(local_tmp_path: Path) -> None:
    client, _ = _client(local_tmp_path)
    with client:
        assert client.post("/api/auth/setup", json={"passphrase": PASSPHRASE}).status_code == 200
        missing_response = client.get("/api/connections/conn_missing/schema")
        create_response = client.post("/api/connections", json=_connection_payload())
        connection_id = create_response.json()["id"]
        assert client.post("/api/auth/lock").status_code == 200
        locked_response = client.post(f"/api/connections/{connection_id}/schema/refresh")

    assert missing_response.status_code == 404
    assert locked_response.status_code == 401
    _assert_redacted(missing_response.text + locked_response.text)


def test_schema_refresh_failure_preserves_cached_snapshot(local_tmp_path: Path) -> None:
    client, introspector = _client(local_tmp_path)
    with client:
        assert client.post("/api/auth/setup", json={"passphrase": PASSPHRASE}).status_code == 200
        create_response = client.post("/api/connections", json=_connection_payload())
        connection_id = create_response.json()["id"]
        first_response = client.post(f"/api/connections/{connection_id}/schema/refresh")
        introspector.fail = True
        failed_response = client.post(f"/api/connections/{connection_id}/schema/refresh")
        cached_response = client.get(f"/api/connections/{connection_id}/schema")

    assert first_response.status_code == 200
    assert failed_response.status_code == 502
    assert cached_response.json()["snapshot"] == first_response.json()["snapshot"]
    _assert_redacted(failed_response.text + cached_response.text)
