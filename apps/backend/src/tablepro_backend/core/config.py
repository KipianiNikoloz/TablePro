from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal, Self

from pydantic import model_validator
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
    auth_cookie_name: str = "tablepro_session"
    auth_session_idle_timeout_seconds: int = 30 * 60
    auth_session_cookie_secure: bool = False
    auth_session_cookie_samesite: Literal["lax", "strict", "none"] = "lax"
    vault_passphrase_min_length: int = 12
    vault_kdf_algorithm: str = "pbkdf2-sha256"
    vault_kdf_iterations: int = 1_200_000
    query_default_row_limit: int = 1000
    query_default_page_size: int = 100
    query_max_page_size: int = 500
    query_timeout_seconds: int = 30
    query_max_concurrent_jobs: int = 4
    query_result_store_max_rows: int = 10_000
    query_pane_session_idle_timeout_seconds: int = 30 * 60

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
