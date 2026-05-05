from __future__ import annotations

from pathlib import Path

from tablepro_backend.core.config import Settings


def test_settings_defaults_sqlite_path_under_data_dir() -> None:
    settings = Settings(data_dir=Path("local-data"))

    assert settings.app_name == "TablePro Backend"
    assert settings.environment == "local"
    assert settings.sqlite_path == Path("local-data") / "tablepro.sqlite3"
    assert settings.sqlite_url.endswith("local-data/tablepro.sqlite3")


def test_settings_accepts_explicit_sqlite_path(local_tmp_path: Path) -> None:
    sqlite_path = local_tmp_path / "app.sqlite3"

    settings = Settings(data_dir=local_tmp_path / "data", sqlite_path=sqlite_path)

    assert settings.sqlite_path == sqlite_path
