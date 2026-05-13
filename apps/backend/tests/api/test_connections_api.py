from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from tablepro_backend.application.services.connections import ConnectionService
from tablepro_backend.core.config import Settings
from tablepro_backend.domain.connections import ConnectionTestRequest, ConnectionTestResult
from tablepro_backend.infrastructure.database.connections import SQLiteConnectionRepository
from tablepro_backend.main import create_app

PASSPHRASE = "correct horse battery staple"


class FakeConnectionTester:
    def __init__(self, ok: bool = True) -> None:
        self.ok = ok
        self.requests: list[ConnectionTestRequest] = []

    def test(self, request: ConnectionTestRequest) -> ConnectionTestResult:
        self.requests.append(request)
        return ConnectionTestResult(
            ok=self.ok,
            dialect=request.dialect,
            message="fake ok" if self.ok else "fake failed",
        )


def _client(local_tmp_path: Path) -> tuple[TestClient, FakeConnectionTester]:
    settings = Settings(
        data_dir=local_tmp_path,
        sqlite_path=local_tmp_path / "tablepro.sqlite3",
        vault_kdf_iterations=1000,
    )
    app = create_app(settings)
    tester = FakeConnectionTester()
    app.state.connection_service = ConnectionService(
        SQLiteConnectionRepository(settings),
        app.state.vault_service,
        tester,
    )
    return TestClient(app), tester


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
    assert "saved-password" not in lowered
    assert "secret_ref" not in lowered
    assert "ciphertext" not in lowered
    assert "sec_" not in lowered


def test_connection_apis_require_auth(local_tmp_path: Path) -> None:
    client, _ = _client(local_tmp_path)
    with client:
        response = client.get("/api/connections")

    assert response.status_code == 401


def test_connection_api_creates_lists_gets_updates_and_deletes(local_tmp_path: Path) -> None:
    client, _ = _client(local_tmp_path)
    with client:
        assert client.post("/api/auth/setup", json={"passphrase": PASSPHRASE}).status_code == 200
        create_response = client.post("/api/connections", json=_connection_payload())
        connection_id = create_response.json()["id"]
        list_response = client.get("/api/connections")
        get_response = client.get(f"/api/connections/{connection_id}")
        update_response = client.patch(
            f"/api/connections/{connection_id}",
            json={"name": "Renamed", "password": "saved-password"},
        )
        delete_response = client.delete(f"/api/connections/{connection_id}")
        list_after_delete = client.get("/api/connections")

    assert create_response.status_code == 200
    assert create_response.json()["has_password"] is True
    assert list_response.json()["connections"][0]["id"] == connection_id
    assert get_response.json()["name"] == "Local Postgres"
    assert update_response.json()["name"] == "Renamed"
    assert delete_response.status_code == 204
    assert list_after_delete.json() == {"connections": []}
    _assert_redacted(
        " ".join(
            [
                create_response.text,
                list_response.text,
                get_response.text,
                update_response.text,
                delete_response.text,
            ]
        )
    )


def test_connection_credential_operations_require_unlocked_vault(local_tmp_path: Path) -> None:
    client, _ = _client(local_tmp_path)
    with client:
        assert client.post("/api/auth/setup", json={"passphrase": PASSPHRASE}).status_code == 200
        create_response = client.post("/api/connections", json=_connection_payload())
        connection_id = create_response.json()["id"]
        assert client.post("/api/auth/lock").status_code == 200

        list_response = client.get("/api/connections")
        create_locked = client.post("/api/connections", json=_connection_payload())
        update_locked = client.patch(
            f"/api/connections/{connection_id}",
            json={"password": "saved-password"},
        )
        test_locked = client.post(f"/api/connections/{connection_id}/test")

    assert list_response.status_code == 401
    assert create_locked.status_code == 401
    assert update_locked.status_code == 401
    assert test_locked.status_code == 401


def test_connection_test_uses_fake_adapter_and_redacts_password(local_tmp_path: Path) -> None:
    client, tester = _client(local_tmp_path)
    with client:
        assert client.post("/api/auth/setup", json={"passphrase": PASSPHRASE}).status_code == 200
        provided_response = client.post("/api/connections/test", json=_connection_payload("db-password"))
        create_response = client.post("/api/connections", json=_connection_payload("saved-password"))
        saved_response = client.post(f"/api/connections/{create_response.json()['id']}/test")

    assert provided_response.status_code == 200
    assert provided_response.json() == {"ok": True, "dialect": "postgres", "message": "fake ok"}
    assert saved_response.status_code == 200
    assert tester.requests[0].password == "db-password"
    assert tester.requests[1].password == "saved-password"
    _assert_redacted(provided_response.text + saved_response.text)


def test_connection_api_rejects_unsupported_dialect(local_tmp_path: Path) -> None:
    client, _ = _client(local_tmp_path)
    payload = _connection_payload()
    payload["dialect"] = "sqlite"

    with client:
        assert client.post("/api/auth/setup", json={"passphrase": PASSPHRASE}).status_code == 200
        response = client.post("/api/connections", json=payload)

    assert response.status_code == 422
    _assert_redacted(response.text)
