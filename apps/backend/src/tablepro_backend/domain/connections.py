from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

ConnectionDialect = Literal["postgres", "mysql"]


class ConnectionError(Exception):
    """Base class for saved database connection errors."""


class ConnectionNotFoundError(ConnectionError):
    """Raised when a saved connection cannot be found."""


class ConnectionValidationError(ConnectionError):
    """Raised when connection input is invalid."""


@dataclass(frozen=True)
class ConnectionInput:
    name: str
    dialect: ConnectionDialect
    host: str
    port: int
    database: str
    username: str
    password: str
    environment_label: str


@dataclass(frozen=True)
class ConnectionUpdate:
    name: str | None = None
    host: str | None = None
    port: int | None = None
    database: str | None = None
    username: str | None = None
    password: str | None = None
    environment_label: str | None = None


@dataclass(frozen=True)
class SavedConnection:
    id: str
    name: str
    dialect: ConnectionDialect
    host: str
    port: int
    database: str
    username: str
    environment_label: str
    password_secret_ref: str
    created_at: datetime
    updated_at: datetime

    @property
    def has_password(self) -> bool:
        return bool(self.password_secret_ref)


@dataclass(frozen=True)
class ConnectionTestRequest:
    dialect: ConnectionDialect
    host: str
    port: int
    database: str
    username: str
    password: str


@dataclass(frozen=True)
class ConnectionTestResult:
    ok: bool
    dialect: ConnectionDialect
    message: str
