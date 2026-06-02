from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

from tablepro_backend.domain.connections import ConnectionDialect

QueryJobStatus = Literal["pending", "running", "succeeded", "failed", "cancelled"]
PaneTransactionState = Literal["idle", "in_transaction", "unknown"]


class QueryError(Exception):
    """Base class for query execution errors."""


class QueryJobNotFoundError(QueryError):
    """Raised when a query job cannot be found."""


class QueryResultNotFoundError(QueryError):
    """Raised when a query result page cannot be found."""


class QueryValidationError(QueryError):
    """Raised when query input is invalid."""


@dataclass(frozen=True)
class QuerySubmit:
    connection_id: str
    pane_id: str
    sql: str
    page_size: int | None = None
    row_limit: int | None = None


@dataclass(frozen=True)
class QueryConnectionDetails:
    connection_id: str
    dialect: ConnectionDialect
    host: str
    port: int
    database: str
    username: str
    password: str


@dataclass(frozen=True)
class QueryRunRequest:
    job_id: str
    pane_id: str
    sql: str
    row_limit: int
    timeout_seconds: int


@dataclass(frozen=True)
class QueryColumn:
    name: str
    data_type: str | None = None


@dataclass(frozen=True)
class QueryExecutionError:
    code: str
    message: str
    category: str = "database"


@dataclass(frozen=True)
class QueryExecutionResult:
    columns: list[QueryColumn]
    rows: list[list[Any]]
    rows_affected: int | None
    transaction_state: PaneTransactionState = "unknown"
    limit_reached: bool = False

    @property
    def has_result_set(self) -> bool:
        return bool(self.columns)


@dataclass(frozen=True)
class QueryResultPage:
    job_id: str
    page_index: int
    page_size: int
    total_rows: int
    columns: list[QueryColumn]
    rows: list[list[Any]]
    limit_reached: bool


@dataclass(frozen=True)
class QueryJob:
    id: str
    connection_id: str
    pane_id: str
    status: QueryJobStatus
    submitted_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: int | None = None
    row_count: int | None = None
    rows_affected: int | None = None
    result_handle: str | None = None
    page_size: int | None = None
    total_rows: int | None = None
    limit_reached: bool = False
    transaction_state: PaneTransactionState = "unknown"
    error: QueryExecutionError | None = None


@dataclass
class PaneSession:
    connection_id: str
    pane_id: str
    dialect: ConnectionDialect
    handle: object
    transaction_state: PaneTransactionState = "unknown"
