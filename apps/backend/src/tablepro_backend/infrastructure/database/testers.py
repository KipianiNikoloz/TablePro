from __future__ import annotations

from tablepro_backend.domain.connections import (
    ConnectionTestRequest,
    ConnectionTestResult,
    ConnectionValidationError,
)


class DriverConnectionTester:
    def test(self, request: ConnectionTestRequest) -> ConnectionTestResult:
        if request.dialect == "postgres":
            return self._test_postgres(request)
        if request.dialect == "mysql":
            return self._test_mysql(request)
        raise ConnectionValidationError("Unsupported database dialect.")

    def _test_postgres(self, request: ConnectionTestRequest) -> ConnectionTestResult:
        try:
            import psycopg

            with psycopg.connect(
                host=request.host,
                port=request.port,
                dbname=request.database,
                user=request.username,
                password=request.password,
                connect_timeout=5,
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
        except Exception:
            return ConnectionTestResult(
                ok=False,
                dialect=request.dialect,
                message="Connection test failed.",
            )
        return ConnectionTestResult(
            ok=True, dialect=request.dialect, message="Connection test passed."
        )

    def _test_mysql(self, request: ConnectionTestRequest) -> ConnectionTestResult:
        connection = None
        try:
            import pymysql

            connection = pymysql.connect(
                host=request.host,
                port=request.port,
                database=request.database,
                user=request.username,
                password=request.password,
                connect_timeout=5,
                read_timeout=5,
                write_timeout=5,
            )
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except Exception:
            return ConnectionTestResult(
                ok=False,
                dialect=request.dialect,
                message="Connection test failed.",
            )
        finally:
            if connection is not None:
                connection.close()
        return ConnectionTestResult(
            ok=True, dialect=request.dialect, message="Connection test passed."
        )
