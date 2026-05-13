from __future__ import annotations

from tablepro_backend.application.services.vault import VaultService
from tablepro_backend.domain.auth import VaultLockedError
from tablepro_backend.domain.connections import (
    ConnectionInput,
    ConnectionTestRequest,
    ConnectionTestResult,
    ConnectionUpdate,
    ConnectionValidationError,
    SavedConnection,
)
from tablepro_backend.infrastructure.database.connections import SQLiteConnectionRepository
from tablepro_backend.ports.connections import ConnectionTester


class ConnectionService:
    def __init__(
        self,
        repository: SQLiteConnectionRepository,
        vault: VaultService,
        tester: ConnectionTester,
    ) -> None:
        self.repository = repository
        self.vault = vault
        self.tester = tester

    def create(self, data: ConnectionInput) -> SavedConnection:
        self._validate_connection_values(data.host, data.port, data.name, data.environment_label)
        secret_ref = self.vault.create_secret_ref(
            data.password,
            label=f"connection:{data.name}",
            secret_type="database_password",
        )
        return self.repository.create(data, secret_ref)

    def list(self) -> list[SavedConnection]:
        return self.repository.list()

    def get(self, connection_id: str) -> SavedConnection:
        return self.repository.get(connection_id)

    def update(self, connection_id: str, update: ConnectionUpdate) -> SavedConnection:
        current = self.repository.get(connection_id)
        self._validate_connection_values(
            update.host if update.host is not None else current.host,
            update.port if update.port is not None else current.port,
            update.name if update.name is not None else current.name,
            update.environment_label
            if update.environment_label is not None
            else current.environment_label,
        )
        new_secret_ref = None
        if update.password is not None:
            self._require_unlocked()
            new_secret_ref = self.vault.create_secret_ref(
                update.password,
                label=f"connection:{update.name or current.name}",
                secret_type="database_password",
            )
        refs = self.repository.update(connection_id, update, password_secret_ref=new_secret_ref)
        if refs.previous:
            self.vault.delete_secret_ref(refs.previous)
        return self.repository.get(connection_id)

    def delete(self, connection_id: str) -> None:
        self._require_unlocked()
        secret_ref = self.repository.delete(connection_id)
        self.vault.delete_secret_ref(secret_ref)

    def test_provided(self, request: ConnectionTestRequest) -> ConnectionTestResult:
        self._require_unlocked()
        self._validate_connection_values(request.host, request.port, "test", "test")
        return self.tester.test(request)

    def test_saved(self, connection_id: str) -> ConnectionTestResult:
        self._require_unlocked()
        connection = self.repository.get(connection_id)
        password = self.vault.resolve_secret_ref(connection.password_secret_ref)
        return self.tester.test(
            ConnectionTestRequest(
                dialect=connection.dialect,
                host=connection.host,
                port=connection.port,
                database=connection.database,
                username=connection.username,
                password=password,
            )
        )

    def _require_unlocked(self) -> None:
        if not self.vault.is_unlocked():
            raise VaultLockedError("Vault is locked.")

    def _validate_connection_values(
        self,
        host: str,
        port: int,
        name: str,
        environment_label: str,
    ) -> None:
        if not name.strip():
            raise ConnectionValidationError("Connection name is required.")
        if not host.strip():
            raise ConnectionValidationError("Connection host is required.")
        if not environment_label.strip():
            raise ConnectionValidationError("Environment label is required.")
        if port < 1 or port > 65535:
            raise ConnectionValidationError("Connection port must be between 1 and 65535.")
