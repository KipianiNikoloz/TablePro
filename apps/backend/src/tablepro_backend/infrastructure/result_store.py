from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from uuid import uuid4

from tablepro_backend.domain.query import (
    QueryColumn,
    QueryResultNotFoundError,
    QueryResultPage,
)


@dataclass(frozen=True)
class StoredResult:
    job_id: str
    columns: list[QueryColumn]
    rows: list[list[object]]
    page_size: int
    limit_reached: bool


class InMemoryResultStore:
    def __init__(self, *, max_rows: int) -> None:
        self.max_rows = max_rows
        self._results: dict[str, StoredResult] = {}
        self._order: list[str] = []
        self._lock = Lock()

    def store(
        self,
        *,
        job_id: str,
        columns: list[QueryColumn],
        rows: list[list[object]],
        page_size: int,
        limit_reached: bool,
    ) -> str:
        handle = f"res_{uuid4().hex}"
        stored = StoredResult(
            job_id=job_id,
            columns=columns,
            rows=rows,
            page_size=page_size,
            limit_reached=limit_reached,
        )
        with self._lock:
            self._results[handle] = stored
            self._order.append(handle)
            self._evict_to_limit()
        return handle

    def page(self, handle: str, *, job_id: str, page_index: int) -> QueryResultPage:
        if page_index < 0:
            raise QueryResultNotFoundError("Result page was not found.")
        with self._lock:
            stored = self._results.get(handle)
            if stored is None or stored.job_id != job_id:
                raise QueryResultNotFoundError("Result page was not found.")
            start = page_index * stored.page_size
            end = start + stored.page_size
            if start >= len(stored.rows) and (page_index != 0 or stored.rows):
                raise QueryResultNotFoundError("Result page was not found.")
            rows = stored.rows[start:end]
            return QueryResultPage(
                job_id=job_id,
                page_index=page_index,
                page_size=stored.page_size,
                total_rows=len(stored.rows),
                columns=stored.columns,
                rows=rows,
                limit_reached=stored.limit_reached,
            )

    def _evict_to_limit(self) -> None:
        while self._total_rows() > self.max_rows and self._order:
            oldest = self._order.pop(0)
            self._results.pop(oldest, None)

    def _total_rows(self) -> int:
        return sum(len(result.rows) for result in self._results.values())
