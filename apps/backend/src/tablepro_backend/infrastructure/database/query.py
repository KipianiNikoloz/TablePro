from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tablepro_backend.domain.connections import ConnectionValidationError
from tablepro_backend.domain.query import (
    PaneSession,
    PaneTransactionState,
    QueryColumn,
    QueryConnectionDetails,
    QueryExecutionResult,
    QueryRunRequest,
)


@dataclass
class DriverQuerySession:
    dialect: str
    connection: Any


class DriverQueryAdapter:
    def open_session(self, connection: QueryConnectionDetails) -> DriverQuerySession:
        if connection.dialect == "postgres":
            return self._open_postgres(connection)
        if connection.dialect == "mysql":
            return self._open_mysql(connection)
        raise ConnectionValidationError("Unsupported database dialect.")

    def execute(self, session: PaneSession, request: QueryRunRequest) -> QueryExecutionResult:
        if session.dialect == "postgres":
            return self._execute_postgres(session.handle, request)
        if session.dialect == "mysql":
            return self._execute_mysql(session.handle, request)
        raise ConnectionValidationError("Unsupported database dialect.")

    def cancel(self, session: PaneSession) -> None:
        handle = session.handle
        try:
            if session.dialect == "postgres":
                handle.connection.cancel()
            elif session.dialect == "mysql":
                handle.connection.close()
        except Exception:
            return

    def close(self, session: PaneSession) -> None:
        try:
            session.handle.connection.close()
        except Exception:
            return

    def _open_postgres(self, details: QueryConnectionDetails) -> DriverQuerySession:
        import psycopg

        connection = psycopg.connect(
            host=details.host,
            port=details.port,
            dbname=details.database,
            user=details.username,
            password=details.password,
            connect_timeout=5,
            autocommit=True,
        )
        return DriverQuerySession(dialect="postgres", connection=connection)

    def _open_mysql(self, details: QueryConnectionDetails) -> DriverQuerySession:
        import pymysql

        connection = pymysql.connect(
            host=details.host,
            port=details.port,
            database=details.database,
            user=details.username,
            password=details.password,
            connect_timeout=5,
            read_timeout=30,
            write_timeout=30,
            autocommit=True,
        )
        return DriverQuerySession(dialect="mysql", connection=connection)

    def _execute_postgres(
        self,
        session: DriverQuerySession,
        request: QueryRunRequest,
    ) -> QueryExecutionResult:
        with session.connection.cursor() as cursor:
            cursor.execute(request.sql)
            rows: list[list[object]] = []
            columns: list[QueryColumn] = []
            limit_reached = False
            if cursor.description:
                columns = [
                    QueryColumn(name=description.name, data_type=str(description.type_code))
                    for description in cursor.description
                ]
                fetched = cursor.fetchmany(request.row_limit + 1)
                limit_reached = len(fetched) > request.row_limit
                rows = [list(row) for row in fetched[: request.row_limit]]
            return QueryExecutionResult(
                columns=columns,
                rows=rows,
                rows_affected=_rows_affected(cursor.rowcount),
                transaction_state=_transaction_state(request.sql),
                limit_reached=limit_reached,
            )

    def _execute_mysql(
        self,
        session: DriverQuerySession,
        request: QueryRunRequest,
    ) -> QueryExecutionResult:
        with session.connection.cursor() as cursor:
            cursor.execute(request.sql)
            rows: list[list[object]] = []
            columns: list[QueryColumn] = []
            limit_reached = False
            if cursor.description:
                columns = [
                    QueryColumn(name=description[0], data_type=str(description[1]))
                    for description in cursor.description
                ]
                fetched = cursor.fetchmany(request.row_limit + 1)
                limit_reached = len(fetched) > request.row_limit
                rows = [list(row) for row in fetched[: request.row_limit]]
            return QueryExecutionResult(
                columns=columns,
                rows=rows,
                rows_affected=_rows_affected(cursor.rowcount),
                transaction_state=_transaction_state(request.sql),
                limit_reached=limit_reached,
            )


def _rows_affected(rowcount: int) -> int | None:
    return rowcount if rowcount >= 0 else None


def _transaction_state(sql: str) -> PaneTransactionState:
    first = sql.strip().split(None, 1)[0].lower() if sql.strip() else ""
    if first == "begin":
        return "in_transaction"
    if first in {"commit", "rollback"}:
        return "idle"
    return "unknown"
