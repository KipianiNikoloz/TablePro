from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from tablepro_backend import __version__


class Settings(BaseSettings):
    app_name: str = "TablePro Backend"
    app_version: str = __version__
    environment: str = "local"
    log_level: str = "INFO"
    data_dir: Path = Path("data")
    sqlite_path: Path | None = None
    apply_migrations_on_startup: bool = True

    model_config = SettingsConfigDict(
        env_prefix="TABLEPRO_",
        env_file=".env",
        extra="ignore",
    )

    @model_validator(mode="after")
    def default_sqlite_path(self) -> Self:
        if self.sqlite_path is None:
            self.sqlite_path = self.data_dir / "tablepro.sqlite3"
        return self

    @property
    def sqlite_url(self) -> str:
        return f"sqlite:///{self.sqlite_path.as_posix()}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
