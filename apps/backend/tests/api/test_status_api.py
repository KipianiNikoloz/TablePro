from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from tablepro_backend.core.config import Settings
from tablepro_backend.main import create_app


def test_healthz_does_not_require_database(local_tmp_path: Path) -> None:
    settings = Settings(
        data_dir=local_tmp_path,
        sqlite_path=local_tmp_path / "tablepro.sqlite3",
        apply_migrations_on_startup=False,
    )
    client = TestClient(create_app(settings))

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readyz_reports_ready_after_startup_migrations(local_tmp_path: Path) -> None:
    settings = Settings(data_dir=local_tmp_path, sqlite_path=local_tmp_path / "tablepro.sqlite3")

    with TestClient(create_app(settings)) as client:
        response = client.get("/readyz")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["checks"][0]["name"] == "app_database"
    assert body["checks"][0]["status"] == "pass"
    assert body["checks"][0]["details"]["current_revision"] == "202605130002"


def test_readyz_reports_not_ready_without_startup_migrations(local_tmp_path: Path) -> None:
    settings = Settings(
        data_dir=local_tmp_path,
        sqlite_path=local_tmp_path / "tablepro.sqlite3",
        apply_migrations_on_startup=False,
    )

    with TestClient(create_app(settings)) as client:
        response = client.get("/readyz")

    assert response.status_code == 200
    assert response.json()["status"] == "not_ready"


def test_runtime_metadata_redacts_paths_and_secret_like_values(local_tmp_path: Path) -> None:
    settings = Settings(
        environment="local",
        data_dir=local_tmp_path / "secret-password-dir",
        sqlite_path=local_tmp_path / "secret-password-dir" / "credential-token.sqlite3",
    )

    with TestClient(create_app(settings)) as client:
        response = client.get("/api/runtime")

    assert response.status_code == 200
    body = response.json()
    serialized = response.text.lower()
    assert body["vault_status"] == "uninitialized"
    assert body["data_dir_configured"] is True
    assert body["sqlite_configured"] is True
    assert "secret" not in serialized
    assert "password" not in serialized
    assert "credential-token" not in serialized
    assert str(local_tmp_path).lower() not in serialized


def test_runtime_metadata_does_not_require_migrated_vault_tables(local_tmp_path: Path) -> None:
    settings = Settings(
        data_dir=local_tmp_path,
        sqlite_path=local_tmp_path / "tablepro.sqlite3",
        apply_migrations_on_startup=False,
    )

    with TestClient(create_app(settings)) as client:
        response = client.get("/api/runtime")

    assert response.status_code == 200
    assert response.json()["vault_status"] == "uninitialized"
