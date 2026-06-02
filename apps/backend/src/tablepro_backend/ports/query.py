from __future__ import annotations

from typing import Protocol

from tablepro_backend.domain.query import (
    PaneSession,
    QueryConnectionDetails,
    QueryExecutionResult,
    QueryRunRequest,
)


class QueryAdapter(Protocol):
    def open_session(self, connection: QueryConnectionDetails) -> object:
        """Open a dialect-specific database session for a saved connection."""

    def execute(self, session: PaneSession, request: QueryRunRequest) -> QueryExecutionResult:
        """Execute SQL in a pane-scoped session."""

    def cancel(self, session: PaneSession) -> None:
        """Request cancellation for the current statement in the session."""

    def close(self, session: PaneSession) -> None:
        """Close a pane-scoped database session."""
