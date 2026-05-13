from __future__ import annotations

from pathlib import Path
import sqlite3

import pytest

from tablepro_backend.application.services.connections import ConnectionService
from tablepro_backend.application.services.vault import VaultService
from tablepro_backend.core.config import Settings
from tablepro_backend.domain.auth import SecretRefNotFoundError, VaultLockedError
from tablepro_backend.domain.connections import (
    ConnectionInput,
    ConnectionTestRequest,
    ConnectionTestResult,
    ConnectionUpdate,
)
from tablepro_backend.infrastructure.database.connections import SQLiteConnectionRepository
from tablepro_backend.infrastructure.database.migrations import apply_app_migrations
from tablepro_backend.infrastructure.database.vault import SQLiteVaultRepository

PASSPHRASE = "correct horse battery staple"


class FakeConnectionTester:
    def __init__(self) -> None:
        self.requests: list[ConnectionTestRequest] = []

    def test(self, request: ConnectionTestRequest) -> ConnectionTestResult:
        self.requests.append(request)
        return ConnectionTestResult(ok=True, dialect=request.dialect, message="fake ok")


def _service(local_tmp_path: Path) -> tuple[ConnectionService, VaultService, FakeConnectionTester]:
    settings = Settings(
        data_dir=local_tmp_path,
        sqlite_path=local_tmp_path / "tablepro.sqlite3",
        vault_kdf_iterations=1000,
    )
    apply_app_migrations(settings)
    vault_repository = SQLiteVaultRepository(settings)
    vault = VaultService(settings, vault_repository)
    vault.initialize(PASSPHRASE)
    tester = FakeConnectionTester()
    service = ConnectionService(SQLiteConnectionRepository(settings), vault, tester)
    return service, vault, tester


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


def test_connection_service_creates_lists_and_redacts_secret_ref(local_tmp_path: Path) -> None:
    service, vault, _ = _service(local_tmp_path)

    saved = service.create(_connection_input())
    listed = service.list()

    assert saved.id.startswith("conn_")
    assert listed == [saved]
    assert saved.has_password is True
    assert vault.resolve_secret_ref(saved.password_secret_ref) == "db-password"

    with sqlite3.connect(local_tmp_path / "tablepro.sqlite3") as connection:
        ciphertext = connection.execute("SELECT ciphertext FROM secret_refs").fetchone()[0]
        connection_row = connection.execute(
            "SELECT password_secret_ref FROM database_connections"
        ).fetchone()

    assert "db-password" not in ciphertext
    assert connection_row[0].startswith("sec_")


def test_connection_service_updates_password_and_removes_old_secret(local_tmp_path: Path) -> None:
    service, vault, _ = _service(local_tmp_path)
    saved = service.create(_connection_input("old-password"))

    updated = service.update(saved.id, ConnectionUpdate(password="new-password", name="Renamed"))

    assert updated.name == "Renamed"
    assert vault.resolve_secret_ref(updated.password_secret_ref) == "new-password"
    with pytest.raises(SecretRefNotFoundError):
        vault.resolve_secret_ref(saved.password_secret_ref)


def test_connection_service_rejects_password_operations_when_locked(local_tmp_path: Path) -> None:
    service, vault, _ = _service(local_tmp_path)
    saved = service.create(_connection_input())
    vault.lock()

    assert service.list() == [saved]
    with pytest.raises(VaultLockedError):
        service.create(_connection_input())
    with pytest.raises(VaultLockedError):
        service.update(saved.id, ConnectionUpdate(password="new-password"))
    with pytest.raises(VaultLockedError):
        service.delete(saved.id)


def test_connection_service_tests_saved_connection_with_resolved_password(
    local_tmp_path: Path,
) -> None:
    service, _, tester = _service(local_tmp_path)
    saved = service.create(_connection_input("saved-password"))

    result = service.test_saved(saved.id)

    assert result.ok is True
    assert tester.requests[0].password == "saved-password"
    assert tester.requests[0].database == "app"
