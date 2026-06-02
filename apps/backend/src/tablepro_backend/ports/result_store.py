from __future__ import annotations

from typing import Protocol

from tablepro_backend.domain.query import QueryColumn, QueryResultPage


class ResultStore(Protocol):
    def store(
        self,
        *,
        job_id: str,
        columns: list[QueryColumn],
        rows: list[list[object]],
        page_size: int,
        limit_reached: bool,
    ) -> str:
        """Store temporary result rows and return a result handle."""

    def page(self, handle: str, *, job_id: str, page_index: int) -> QueryResultPage:
        """Return one page from a temporary result handle."""
