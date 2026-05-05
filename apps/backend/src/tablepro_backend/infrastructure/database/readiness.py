from __future__ import annotations

from alembic.script import ScriptDirectory
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import Connection
from alembic.runtime.migration import MigrationContext

from tablepro_backend.core.config import Settings
from tablepro_backend.domain.readiness import AppDatabaseReadiness
from tablepro_backend.infrastructure.database.migrations import build_alembic_config


def check_app_database(settings: Settings) -> AppDatabaseReadiness:
    database_exists = settings.sqlite_path.exists()
    try:
        engine = create_engine(settings.sqlite_url)
        with engine.connect() as connection:
            current_revision = _current_revision(connection)
        head_revision = ScriptDirectory.from_config(build_alembic_config(settings)).get_current_head()
    except SQLAlchemyError as exc:
        return AppDatabaseReadiness(
            ready=False,
            message=f"App database is not reachable: {exc.__class__.__name__}",
            database_exists=database_exists,
            current_revision=None,
            head_revision=None,
        )

    ready = current_revision == head_revision and current_revision is not None
    message = "App database is migrated" if ready else "App database migration is not current"
    return AppDatabaseReadiness(
        ready=ready,
        message=message,
        database_exists=database_exists,
        current_revision=current_revision,
        head_revision=head_revision,
    )


def _current_revision(connection: Connection) -> str | None:
    return MigrationContext.configure(connection).get_current_revision()
