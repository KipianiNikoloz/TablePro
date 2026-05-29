from __future__ import annotations

from tablepro_backend.application.services.vault import VaultService
from tablepro_backend.domain.auth import VaultLockedError
from tablepro_backend.domain.connections import ConnectionNotFoundError
from tablepro_backend.domain.schema import (
    SchemaIntrospectionRequest,
    SchemaRefreshError,
    SchemaSnapshot,
    SchemaSnapshotNotFoundError,
)
from tablepro_backend.infrastructure.database.connections import SQLiteConnectionRepository
from tablepro_backend.infrastructure.database.schema import SQLiteSchemaRepository
from tablepro_backend.ports.schema import SchemaIntrospector


class SchemaService:
    def __init__(
        self,
        connection_repository: SQLiteConnectionRepository,
        schema_repository: SQLiteSchemaRepository,
        vault: VaultService,
        introspector: SchemaIntrospector,
    ) -> None:
        self.connection_repository = connection_repository
        self.schema_repository = schema_repository
        self.vault = vault
        self.introspector = introspector

    def get_cached(self, connection_id: str) -> SchemaSnapshot:
        self.connection_repository.get(connection_id)
        return self.schema_repository.get_latest(connection_id)

    def refresh(self, connection_id: str) -> SchemaSnapshot:
        if not self.vault.is_unlocked():
            raise VaultLockedError("Vault is locked.")
        connection = self.connection_repository.get(connection_id)
        password = self.vault.resolve_secret_ref(connection.password_secret_ref)
        try:
            snapshot = self.introspector.introspect(
                SchemaIntrospectionRequest(
                    connection_id=connection.id,
                    dialect=connection.dialect,
                    host=connection.host,
                    port=connection.port,
                    database=connection.database,
                    username=connection.username,
                    password=password,
                )
            )
        except (ConnectionNotFoundError, SchemaSnapshotNotFoundError, VaultLockedError):
            raise
        except Exception as exc:
            raise SchemaRefreshError("Schema refresh failed.") from exc
        return self.schema_repository.save(snapshot)
