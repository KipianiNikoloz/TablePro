from __future__ import annotations

from pathlib import Path
from threading import Event
import time

import pytest

from tablepro_backend.application.services.connections import ConnectionService
from tablepro_backend.application.services.query import QueryService
from tablepro_backend.application.services.vault import VaultService
from tablepro_backend.core.config import Settings
from tablepro_backend.domain.auth import VaultLockedError
from tablepro_backend.domain.connections import (
    ConnectionInput,
    ConnectionTestRequest,
    ConnectionTestResult,
)
from tablepro_backend.domain.query import (
    PaneSession,
    QueryColumn,
    QueryConnectionDetails,
    QueryExecutionResult,
    QueryRunRequest,
    QuerySubmit,
)
from tablepro_backend.infrastructure.database.connections import SQLiteConnectionRepository
from tablepro_backend.infrastructure.database.migrations import apply_app_migrations
from tablepro_backend.infrastructure.database.vault import SQLiteVaultRepository
from tablepro_backend.infrastructure.result_store import InMemoryResultStore

PASSPHRASE = "correct horse battery staple"


class FakeConnectionTester:
    def test(self, request: ConnectionTestRequest) -> ConnectionTestResult:
        return ConnectionTestResult(ok=True, dialect=request.dialect, message="fake ok")


class FakeQueryAdapter:
    def __init__(self, *, fail: bool = False, slow: bool = False) -> None:
        self.fail = fail
        self.slow = slow
        self.cancelled = Event()
        self.opened: list[QueryConnectionDetails] = []
        self.executed: list[tuple[PaneSession, QueryRunRequest]] = []

    def open_session(self, connection: QueryConnectionDetails) -> object:
        self.opened.append(connection)
        return {"session": len(self.opened)}

    def execute(self, session: PaneSession, request: QueryRunRequest) -> QueryExecutionResult:
        self.executed.append((session, request))
        if self.slow:
            self.cancelled.wait(timeout=2)
        if self.fail:
            raise RuntimeError("driver leaked detail")
        return QueryExecutionResult(
            columns=[QueryColumn(name="id", data_type="integer")],
            rows=[[1], [2], [3]],
            rows_affected=None,
            transaction_state="unknown",
        )

    def cancel(self, session: PaneSession) -> None:
        self.cancelled.set()

    def close(self, session: PaneSession) -> None:
        return None


def _settings(local_tmp_path: Path) -> Settings:
    return Settings(
        data_dir=local_tmp_path,
        sqlite_path=local_tmp_path / "tablepro.sqlite3",
        vault_kdf_iterations=1000,
        query_default_page_size=2,
        query_default_row_limit=10,
    )


def _services(
    local_tmp_path: Path,
    adapter: FakeQueryAdapter | None = None,
) -> tuple[QueryService, VaultService, str, FakeQueryAdapter]:
    settings = _settings(local_tmp_path)
    apply_app_migrations(settings)
    vault_repository = SQLiteVaultRepository(settings)
    vault = VaultService(settings, vault_repository)
    vault.initialize(PASSPHRASE)
    connection_repository = SQLiteConnectionRepository(settings)
    connection_service = ConnectionService(connection_repository, vault, FakeConnectionTester())
    saved = connection_service.create(
        ConnectionInput(
            name="Local Postgres",
            dialect="postgres",
            host="localhost",
            port=5432,
            database="app",
            username="app_user",
            password="db-password",
            environment_label="local",
        )
    )
    fake_adapter = adapter or FakeQueryAdapter()
    query_service = QueryService(
        connection_repository,
        vault,
        fake_adapter,
        InMemoryResultStore(max_rows=100),
        settings,
    )
    return query_service, vault, saved.id, fake_adapter


def _wait_for(service: QueryService, job_id: str, status: str) -> None:
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        if service.get(job_id).status == status:
            return
        time.sleep(0.01)
    raise AssertionError(f"Job {job_id} did not reach {status}")


def test_query_service_succeeds_and_pages_results(local_tmp_path: Path) -> None:
    service, _, connection_id, adapter = _services(local_tmp_path)

    job = service.submit(QuerySubmit(connection_id=connection_id, pane_id="pane-a", sql="select 1"))
    _wait_for(service, job.id, "succeeded")
    finished = service.get(job.id)
    first_page = service.page(job.id, 0)
    second_page = service.page(job.id, 1)

    assert finished.row_count == 3
    assert finished.result_handle is not None
    assert first_page.rows == [[1], [2]]
    assert second_page.rows == [[3]]
    assert adapter.executed[0][1].row_limit == 10
    assert adapter.opened[0].password == "db-password"


def test_query_service_fails_with_structured_safe_error(local_tmp_path: Path) -> None:
    service, _, connection_id, _ = _services(local_tmp_path, FakeQueryAdapter(fail=True))

    job = service.submit(QuerySubmit(connection_id=connection_id, pane_id="pane-a", sql="select 1"))
    _wait_for(service, job.id, "failed")
    failed = service.get(job.id)

    assert failed.error is not None
    assert failed.error.code == "query_execution_failed"
    assert "driver leaked detail" not in failed.error.message


def test_query_service_rejects_locked_vault(local_tmp_path: Path) -> None:
    service, vault, connection_id, _ = _services(local_tmp_path)
    vault.lock()

    with pytest.raises(VaultLockedError):
        service.submit(QuerySubmit(connection_id=connection_id, pane_id="pane-a", sql="select 1"))


def test_query_service_reuses_sessions_per_pane(local_tmp_path: Path) -> None:
    service, _, connection_id, adapter = _services(local_tmp_path)

    first = service.submit(QuerySubmit(connection_id=connection_id, pane_id="pane-a", sql="select 1"))
    _wait_for(service, first.id, "succeeded")
    second = service.submit(QuerySubmit(connection_id=connection_id, pane_id="pane-a", sql="select 2"))
    _wait_for(service, second.id, "succeeded")
    third = service.submit(QuerySubmit(connection_id=connection_id, pane_id="pane-b", sql="select 3"))
    _wait_for(service, third.id, "succeeded")

    assert len(adapter.opened) == 2
    assert adapter.executed[0][0].handle == adapter.executed[1][0].handle
    assert adapter.executed[2][0].pane_id == "pane-b"


def test_query_service_cancels_running_job(local_tmp_path: Path) -> None:
    service, _, connection_id, adapter = _services(local_tmp_path, FakeQueryAdapter(slow=True))

    job = service.submit(QuerySubmit(connection_id=connection_id, pane_id="pane-a", sql="select slow"))
    _wait_for(service, job.id, "running")
    service.cancel(job.id)
    _wait_for(service, job.id, "cancelled")

    assert adapter.cancelled.is_set()
