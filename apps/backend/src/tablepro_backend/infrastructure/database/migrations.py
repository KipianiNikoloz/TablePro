from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config

from tablepro_backend.core.config import Settings


def backend_root() -> Path:
    return Path(__file__).resolve().parents[4]


def build_alembic_config(settings: Settings) -> Config:
    root = backend_root()
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "alembic"))
    config.set_main_option("sqlalchemy.url", settings.sqlite_url)
    config.attributes["skip_logger_config"] = True
    return config


def apply_app_migrations(settings: Settings) -> None:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    command.upgrade(build_alembic_config(settings), "head")
