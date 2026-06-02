from __future__ import annotations

from pathlib import Path
from threading import Event
import time

from fastapi.testclient import TestClient

from tablepro_backend.application.services.query import QueryService
from tablepro_backend.core.config import Settings
from tablepro_backend.domain.query import (
    PaneSession,
    QueryColumn,
    QueryConnectionDetails,
    QueryExecutionResult,
    QueryRunRequest,
)
from tablepro_backend.infrastructure.result_store import InMemoryResultStore
from tablepro_backend.main import create_app

PASSPHRASE = "correct horse battery staple"


class FakeQueryAdapter:
    def __init__(self, *, slow: bool = False) -> None:
        self.slow = slow
        self.cancelled = Event()
        self.requests: list[QueryRunRequest] = []
        self.connections: list[QueryConnectionDetails] = []

    def open_session(self, connection: QueryConnectionDetails) -> object:
        self.connections.append(connection)
        return {"session": len(self.connections)}

    def execute(self, session: PaneSession, request: QueryRunRequest) -> QueryExecutionResult:
        self.requests.append(request)
        if self.slow:
            self.cancelled.wait(timeout=2)
        return QueryExecutionResult(
            columns=[QueryColumn(name="id", data_type="integer")],
            rows=[[1], [2], [3]],
            rows_affected=None,
        )

    def cancel(self, session: PaneSession) -> None:
        self.cancelled.set()

    def close(self, session: PaneSession) -> None:
        return None


def _client(
    local_tmp_path: Path,
    adapter: FakeQueryAdapter | None = None,
) -> tuple[TestClient, FakeQueryAdapter]:
    settings = Settings(
        data_dir=local_tmp_path,
        sqlite_path=local_tmp_path / "tablepro.sqlite3",
        vault_kdf_iterations=1000,
        query_default_page_size=2,
    )
    app = create_app(settings)
    fake = adapter or FakeQueryAdapter()
    app.state.result_store = InMemoryResultStore(max_rows=100)
    app.state.query_service = QueryService(
        app.state.connection_repository,
        app.state.vault_service,
        fake,
        app.state.result_store,
        settings,
    )
    return TestClient(app), fake


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


def _wait_for(client: TestClient, job_id: str, status: str) -> dict[str, object]:
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        response = client.get(f"/api/query/jobs/{job_id}")
        body = response.json()
        if body["status"] == status:
            return body
        time.sleep(0.01)
    raise AssertionError(f"Job {job_id} did not reach {status}")


def _assert_redacted(text: str) -> None:
    lowered = text.lower()
    assert "db-password" not in lowered
    assert "secret_ref" not in lowered
    assert "ciphertext" not in lowered
    assert "sec_" not in lowered


def test_query_api_requires_auth(local_tmp_path: Path) -> None:
    client, _ = _client(local_tmp_path)
    with client:
        response = client.post(
            "/api/query/jobs",
            json={"connection_id": "conn_1", "pane_id": "pane-a", "sql": "select 1"},
        )

    assert response.status_code == 401


def test_query_api_submit_status_and_page(local_tmp_path: Path) -> None:
    client, adapter = _client(local_tmp_path)
    with client:
        assert client.post("/api/auth/setup", json={"passphrase": PASSPHRASE}).status_code == 200
        create = client.post("/api/connections", json=_connection_payload())
        submit = client.post(
            "/api/query/jobs",
            json={
                "connection_id": create.json()["id"],
                "pane_id": "pane-a",
                "sql": "select 1",
            },
        )
        job_id = submit.json()["id"]
        finished = _wait_for(client, job_id, "succeeded")
        page = client.get(f"/api/query/jobs/{job_id}/pages/0")

    assert submit.status_code == 200
    assert finished["has_result"] is True
    assert page.status_code == 200
    assert page.json()["rows"] == [[1], [2]]
    assert adapter.connections[0].password == "db-password"
    _assert_redacted(submit.text + page.text)


def test_query_api_rejects_locked_vault(local_tmp_path: Path) -> None:
    client, _ = _client(local_tmp_path)
    with client:
        assert client.post("/api/auth/setup", json={"passphrase": PASSPHRASE}).status_code == 200
        create = client.post("/api/connections", json=_connection_payload())
        assert client.post("/api/auth/lock").status_code == 200
        response = client.post(
            "/api/query/jobs",
            json={
                "connection_id": create.json()["id"],
                "pane_id": "pane-a",
                "sql": "select 1",
            },
        )

    assert response.status_code == 401
    _assert_redacted(response.text)


def test_query_api_cancel_running_job(local_tmp_path: Path) -> None:
    client, adapter = _client(local_tmp_path, FakeQueryAdapter(slow=True))
    with client:
        assert client.post("/api/auth/setup", json={"passphrase": PASSPHRASE}).status_code == 200
        create = client.post("/api/connections", json=_connection_payload())
        submit = client.post(
            "/api/query/jobs",
            json={
                "connection_id": create.json()["id"],
                "pane_id": "pane-a",
                "sql": "select slow",
            },
        )
        job_id = submit.json()["id"]
        _wait_for(client, job_id, "running")
        cancel = client.post(f"/api/query/jobs/{job_id}/cancel")
        cancelled = _wait_for(client, job_id, "cancelled")

    assert cancel.status_code == 200
    assert cancelled["status"] == "cancelled"
    assert adapter.cancelled.is_set()


def test_query_api_missing_page_returns_404(local_tmp_path: Path) -> None:
    client, _ = _client(local_tmp_path)
    with client:
        assert client.post("/api/auth/setup", json={"passphrase": PASSPHRASE}).status_code == 200
        create = client.post("/api/connections", json=_connection_payload())
        submit = client.post(
            "/api/query/jobs",
            json={
                "connection_id": create.json()["id"],
                "pane_id": "pane-a",
                "sql": "select 1",
            },
        )
        job_id = submit.json()["id"]
        _wait_for(client, job_id, "succeeded")
        response = client.get(f"/api/query/jobs/{job_id}/pages/9")

    assert response.status_code == 404
    _assert_redacted(response.text)
