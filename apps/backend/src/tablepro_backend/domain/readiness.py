from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AppDatabaseReadiness:
    ready: bool
    message: str
    database_exists: bool
    current_revision: str | None
    head_revision: str | None
