from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from tablepro_backend.api.routes import router
from tablepro_backend.application.services.auth import AuthService
from tablepro_backend.application.services.connections import ConnectionService
from tablepro_backend.application.services.query import QueryService
from tablepro_backend.application.services.schema import SchemaService
from tablepro_backend.application.services.vault import VaultService
from tablepro_backend.core.config import Settings, get_settings
from tablepro_backend.core.logging import configure_logging
from tablepro_backend.infrastructure.database.connections import SQLiteConnectionRepository
from tablepro_backend.infrastructure.database.introspection import DriverSchemaIntrospector
from tablepro_backend.infrastructure.database.migrations import apply_app_migrations
from tablepro_backend.infrastructure.database.query import DriverQueryAdapter
from tablepro_backend.infrastructure.database.schema import SQLiteSchemaRepository
from tablepro_backend.infrastructure.database.testers import DriverConnectionTester
from tablepro_backend.infrastructure.database.vault import SQLiteVaultRepository
from tablepro_backend.infrastructure.result_store import InMemoryResultStore


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    configure_logging(app_settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if app_settings.apply_migrations_on_startup:
            apply_app_migrations(app_settings)
        yield

    app = FastAPI(title=app_settings.app_name, version=app_settings.app_version, lifespan=lifespan)
    app.state.settings = app_settings
    vault_repository = SQLiteVaultRepository(app_settings)
    vault_service = VaultService(app_settings, vault_repository)
    app.state.vault_repository = vault_repository
    app.state.vault_service = vault_service
    app.state.auth_service = AuthService(app_settings, vault_repository, vault_service)
    connection_repository = SQLiteConnectionRepository(app_settings)
    app.state.connection_repository = connection_repository
    app.state.connection_service = ConnectionService(
        connection_repository,
        vault_service,
        DriverConnectionTester(),
    )
    schema_repository = SQLiteSchemaRepository(app_settings)
    app.state.schema_repository = schema_repository
    app.state.schema_service = SchemaService(
        connection_repository,
        schema_repository,
        vault_service,
        DriverSchemaIntrospector(),
    )
    app.state.result_store = InMemoryResultStore(
        max_rows=app_settings.query_result_store_max_rows
    )
    app.state.query_service = QueryService(
        connection_repository,
        vault_service,
        DriverQueryAdapter(),
        app.state.result_store,
        app_settings,
    )
    app.include_router(router)
    return app


app = create_app()
