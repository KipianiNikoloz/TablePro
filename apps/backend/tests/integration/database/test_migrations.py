from __future__ import annotations

from pathlib import Path
import sqlite3

from tablepro_backend.core.config import Settings
from tablepro_backend.infrastructure.database.migrations import apply_app_migrations
from tablepro_backend.infrastructure.database.readiness import check_app_database


def test_app_migrations_initialize_sqlite_database(local_tmp_path: Path) -> None:
    settings = Settings(data_dir=local_tmp_path, sqlite_path=local_tmp_path / "tablepro.sqlite3")

    apply_app_migrations(settings)

    readiness = check_app_database(settings)
    assert readiness.ready is True
    assert readiness.current_revision == readiness.head_revision

    with sqlite3.connect(settings.sqlite_path) as connection:
        rows = connection.execute("SELECT key, value FROM app_metadata").fetchall()
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }

    assert ("schema_baseline", "202605010001") in rows
    assert {"vault_state", "auth_sessions", "secret_refs"}.issubset(tables)


def test_readiness_reports_unmigrated_database(local_tmp_path: Path) -> None:
    settings = Settings(data_dir=local_tmp_path, sqlite_path=local_tmp_path / "tablepro.sqlite3")

    readiness = check_app_database(settings)

    assert readiness.ready is False
    assert readiness.current_revision is None
    assert readiness.head_revision == "202605090001"
