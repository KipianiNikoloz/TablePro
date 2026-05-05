from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from tablepro_backend.api.routes import router
from tablepro_backend.core.config import Settings, get_settings
from tablepro_backend.core.logging import configure_logging
from tablepro_backend.infrastructure.database.migrations import apply_app_migrations


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
    app.include_router(router)
    return app


app = create_app()
