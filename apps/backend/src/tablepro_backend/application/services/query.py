from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import UTC, datetime
from threading import Lock
from uuid import uuid4

from tablepro_backend.application.services.vault import VaultService
from tablepro_backend.core.config import Settings
from tablepro_backend.domain.auth import VaultLockedError
from tablepro_backend.domain.query import (
    PaneSession,
    QueryConnectionDetails,
    QueryExecutionError,
    QueryJob,
    QueryJobNotFoundError,
    QueryResultNotFoundError,
    QueryResultPage,
    QueryRunRequest,
    QuerySubmit,
    QueryValidationError,
)
from tablepro_backend.infrastructure.database.connections import SQLiteConnectionRepository
from tablepro_backend.ports.query import QueryAdapter
from tablepro_backend.ports.result_store import ResultStore


class QueryService:
    def __init__(
        self,
        connection_repository: SQLiteConnectionRepository,
        vault: VaultService,
        adapter: QueryAdapter,
        result_store: ResultStore,
        settings: Settings,
    ) -> None:
        self.connection_repository = connection_repository
        self.vault = vault
        self.adapter = adapter
        self.result_store = result_store
        self.settings = settings
        self._executor = ThreadPoolExecutor(max_workers=settings.query_max_concurrent_jobs)
        self._jobs: dict[str, QueryJob] = {}
        self._sessions: dict[tuple[str, str], PaneSession] = {}
        self._job_sessions: dict[str, PaneSession] = {}
        self._cancel_requested: set[str] = set()
        self._lock = Lock()

    def submit(self, request: QuerySubmit) -> QueryJob:
        self._validate_submit(request)
        if not self.vault.is_unlocked():
            raise VaultLockedError("Vault is locked.")
        connection = self.connection_repository.get(request.connection_id)
        password = self.vault.resolve_secret_ref(connection.password_secret_ref)
        job_id = f"job_{uuid4().hex}"
        job = QueryJob(
            id=job_id,
            connection_id=connection.id,
            pane_id=request.pane_id,
            status="pending",
            submitted_at=_utc_now(),
            page_size=self._page_size(request.page_size),
        )
        with self._lock:
            self._jobs[job.id] = job
        details = QueryConnectionDetails(
            connection_id=connection.id,
            dialect=connection.dialect,
            host=connection.host,
            port=connection.port,
            database=connection.database,
            username=connection.username,
            password=password,
        )
        self._executor.submit(self._run_job, job.id, request, details)
        return self.get(job.id)

    def get(self, job_id: str) -> QueryJob:
        with self._lock:
            job = self._jobs.get(job_id)
        if job is None:
            raise QueryJobNotFoundError("Query job was not found.")
        return job

    def cancel(self, job_id: str) -> QueryJob:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                raise QueryJobNotFoundError("Query job was not found.")
            if job.status == "pending":
                job = replace(job, status="cancelled", completed_at=_utc_now(), duration_ms=0)
                self._jobs[job_id] = job
                self._cancel_requested.add(job_id)
                return job
            if job.status != "running":
                return job
            self._cancel_requested.add(job_id)
            session = self._job_sessions.get(job_id)
        if session is not None:
            self.adapter.cancel(session)
        return self.get(job_id)

    def page(self, job_id: str, page_index: int) -> QueryResultPage:
        job = self.get(job_id)
        if job.result_handle is None or job.status != "succeeded":
            raise QueryResultNotFoundError("Result page was not found.")
        return self.result_store.page(job.result_handle, job_id=job.id, page_index=page_index)

    def _run_job(
        self,
        job_id: str,
        request: QuerySubmit,
        connection: QueryConnectionDetails,
    ) -> None:
        started_at = _utc_now()
        with self._lock:
            if job_id in self._cancel_requested:
                self._complete_cancelled(job_id, started_at)
                return
            self._jobs[job_id] = replace(self._jobs[job_id], status="running", started_at=started_at)
        try:
            session = self._session_for(connection, request.pane_id)
            with self._lock:
                self._job_sessions[job_id] = session
            result = self.adapter.execute(
                session,
                QueryRunRequest(
                    job_id=job_id,
                    pane_id=request.pane_id,
                    sql=request.sql,
                    row_limit=request.row_limit or self.settings.query_default_row_limit,
                    timeout_seconds=self.settings.query_timeout_seconds,
                ),
            )
            with self._lock:
                cancelled = job_id in self._cancel_requested
            if cancelled:
                self._complete_cancelled(job_id, started_at)
                return
            result_handle = None
            total_rows = len(result.rows) if result.has_result_set else None
            page_size = self._page_size(request.page_size)
            if result.has_result_set:
                result_handle = self.result_store.store(
                    job_id=job_id,
                    columns=result.columns,
                    rows=result.rows,
                    page_size=page_size,
                    limit_reached=result.limit_reached,
                )
            completed_at = _utc_now()
            with self._lock:
                self._jobs[job_id] = replace(
                    self._jobs[job_id],
                    status="succeeded",
                    completed_at=completed_at,
                    duration_ms=_duration_ms(started_at, completed_at),
                    row_count=total_rows,
                    rows_affected=result.rows_affected,
                    result_handle=result_handle,
                    page_size=page_size if result.has_result_set else None,
                    total_rows=total_rows,
                    limit_reached=result.limit_reached,
                    transaction_state=result.transaction_state,
                )
                session.transaction_state = result.transaction_state
        except Exception as exc:
            completed_at = _utc_now()
            with self._lock:
                status = "cancelled" if job_id in self._cancel_requested else "failed"
                self._jobs[job_id] = replace(
                    self._jobs[job_id],
                    status=status,
                    completed_at=completed_at,
                    duration_ms=_duration_ms(started_at, completed_at),
                    error=None if status == "cancelled" else _query_error(exc),
                )
        finally:
            with self._lock:
                self._job_sessions.pop(job_id, None)
                self._cancel_requested.discard(job_id)

    def _session_for(self, connection: QueryConnectionDetails, pane_id: str) -> PaneSession:
        key = (connection.connection_id, pane_id)
        with self._lock:
            existing = self._sessions.get(key)
            if existing is not None:
                return existing
        handle = self.adapter.open_session(connection)
        session = PaneSession(
            connection_id=connection.connection_id,
            pane_id=pane_id,
            dialect=connection.dialect,
            handle=handle,
        )
        with self._lock:
            return self._sessions.setdefault(key, session)

    def _complete_cancelled(self, job_id: str, started_at: datetime) -> None:
        completed_at = _utc_now()
        self._jobs[job_id] = replace(
            self._jobs[job_id],
            status="cancelled",
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=_duration_ms(started_at, completed_at),
        )

    def _validate_submit(self, request: QuerySubmit) -> None:
        if not request.connection_id.strip():
            raise QueryValidationError("Connection id is required.")
        if not request.pane_id.strip():
            raise QueryValidationError("Pane id is required.")
        if not request.sql.strip():
            raise QueryValidationError("SQL is required.")
        if request.page_size is not None and request.page_size < 1:
            raise QueryValidationError("Page size must be positive.")
        if request.row_limit is not None and request.row_limit < 1:
            raise QueryValidationError("Row limit must be positive.")

    def _page_size(self, requested: int | None) -> int:
        page_size = requested or self.settings.query_default_page_size
        return min(page_size, self.settings.query_max_page_size)


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _duration_ms(started_at: datetime, completed_at: datetime) -> int:
    return int((completed_at - started_at).total_seconds() * 1000)


def _query_error(exc: Exception) -> QueryExecutionError:
    if isinstance(exc, QueryValidationError):
        return QueryExecutionError(code="validation_error", message=str(exc), category="validation")
    return QueryExecutionError(
        code="query_execution_failed",
        message="Query execution failed.",
        category="database",
    )
