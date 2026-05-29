from __future__ import annotations

from collections import defaultdict
from typing import Any

from tablepro_backend.domain.schema import (
    SchemaColumn,
    SchemaIndex,
    SchemaIntrospectionRequest,
    SchemaRefreshError,
    SchemaRelationship,
    SchemaSnapshot,
    SchemaTable,
)
from tablepro_backend.infrastructure.database.vault import utc_now


class DriverSchemaIntrospector:
    def introspect(self, request: SchemaIntrospectionRequest) -> SchemaSnapshot:
        if request.dialect == "postgres":
            return self._introspect_postgres(request)
        if request.dialect == "mysql":
            return self._introspect_mysql(request)
        raise SchemaRefreshError("Unsupported database dialect.")

    def _introspect_postgres(self, request: SchemaIntrospectionRequest) -> SchemaSnapshot:
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
                    columns = self._postgres_columns(cursor)
                    primary_keys = self._postgres_primary_keys(cursor)
                    unique_identities = self._postgres_unique_identities(cursor)
                    indexes = self._postgres_indexes(cursor)
                    relationships = self._postgres_relationships(cursor)
        except Exception as exc:
            raise SchemaRefreshError("Schema refresh failed.") from exc
        return self._build_snapshot(
            request,
            columns,
            primary_keys,
            unique_identities,
            indexes,
            relationships,
        )

    def _introspect_mysql(self, request: SchemaIntrospectionRequest) -> SchemaSnapshot:
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
                cursorclass=pymysql.cursors.DictCursor,
            )
            with connection.cursor() as cursor:
                columns = self._mysql_columns(cursor, request.database)
                primary_keys = self._mysql_primary_keys(cursor, request.database)
                unique_identities = self._mysql_unique_identities(cursor, request.database)
                indexes = self._mysql_indexes(cursor, request.database)
                relationships = self._mysql_relationships(cursor, request.database)
        except Exception as exc:
            raise SchemaRefreshError("Schema refresh failed.") from exc
        finally:
            if connection is not None:
                connection.close()
        return self._build_snapshot(
            request,
            columns,
            primary_keys,
            unique_identities,
            indexes,
            relationships,
        )

    def _build_snapshot(
        self,
        request: SchemaIntrospectionRequest,
        columns: dict[tuple[str, str], list[SchemaColumn]],
        primary_keys: dict[tuple[str, str], list[str]],
        unique_identities: dict[tuple[str, str], list[list[str]]],
        indexes: dict[tuple[str, str], list[SchemaIndex]],
        relationships: dict[tuple[str, str], list[SchemaRelationship]],
    ) -> SchemaSnapshot:
        tables = [
            SchemaTable(
                schema_name=schema_name,
                name=table_name,
                columns=table_columns,
                primary_key=primary_keys.get((schema_name, table_name), []),
                unique_identities=unique_identities.get((schema_name, table_name), []),
                indexes=indexes.get((schema_name, table_name), []),
                relationships=relationships.get((schema_name, table_name), []),
            )
            for (schema_name, table_name), table_columns in sorted(columns.items())
        ]
        return SchemaSnapshot(
            connection_id=request.connection_id,
            dialect=request.dialect,
            refreshed_at=utc_now(),
            tables=tables,
        )

    def _postgres_columns(self, cursor: Any) -> dict[tuple[str, str], list[SchemaColumn]]:
        cursor.execute(
            """
            SELECT table_schema, table_name, column_name, data_type, is_nullable,
                   ordinal_position, column_default
            FROM information_schema.columns
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
            ORDER BY table_schema, table_name, ordinal_position
            """
        )
        columns: dict[tuple[str, str], list[SchemaColumn]] = defaultdict(list)
        for row in cursor.fetchall():
            columns[(row[0], row[1])].append(
                SchemaColumn(
                    name=row[2],
                    data_type=row[3],
                    nullable=row[4] == "YES",
                    ordinal_position=row[5],
                    default=row[6],
                )
            )
        return dict(columns)

    def _postgres_primary_keys(self, cursor: Any) -> dict[tuple[str, str], list[str]]:
        cursor.execute(
            """
            SELECT tc.table_schema, tc.table_name, kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
            ORDER BY tc.table_schema, tc.table_name, kcu.ordinal_position
            """
        )
        keys: dict[tuple[str, str], list[str]] = defaultdict(list)
        for row in cursor.fetchall():
            keys[(row[0], row[1])].append(row[2])
        return dict(keys)

    def _postgres_unique_identities(self, cursor: Any) -> dict[tuple[str, str], list[list[str]]]:
        cursor.execute(
            """
            SELECT tc.table_schema, tc.table_name, tc.constraint_name, kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'UNIQUE'
            ORDER BY tc.table_schema, tc.table_name, tc.constraint_name, kcu.ordinal_position
            """
        )
        grouped: dict[tuple[str, str, str], list[str]] = defaultdict(list)
        for row in cursor.fetchall():
            grouped[(row[0], row[1], row[2])].append(row[3])
        identities: dict[tuple[str, str], list[list[str]]] = defaultdict(list)
        for (schema_name, table_name, _), columns in grouped.items():
            identities[(schema_name, table_name)].append(columns)
        return dict(identities)

    def _postgres_indexes(self, cursor: Any) -> dict[tuple[str, str], list[SchemaIndex]]:
        cursor.execute(
            """
            SELECT schemaname, tablename, indexname, indexdef
            FROM pg_indexes
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY schemaname, tablename, indexname
            """
        )
        indexes: dict[tuple[str, str], list[SchemaIndex]] = defaultdict(list)
        for row in cursor.fetchall():
            indexes[(row[0], row[1])].append(
                SchemaIndex(
                    name=row[2],
                    columns=[],
                    unique="UNIQUE INDEX" in row[3].upper(),
                )
            )
        return dict(indexes)

    def _postgres_relationships(
        self, cursor: Any
    ) -> dict[tuple[str, str], list[SchemaRelationship]]:
        cursor.execute(
            """
            SELECT tc.table_schema, tc.table_name, tc.constraint_name, kcu.column_name,
                   ccu.table_schema AS referenced_schema,
                   ccu.table_name AS referenced_table,
                   ccu.column_name AS referenced_column
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage ccu
              ON ccu.constraint_name = tc.constraint_name
             AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            ORDER BY tc.table_schema, tc.table_name, tc.constraint_name, kcu.ordinal_position
            """
        )
        return self._relationships_from_rows(cursor.fetchall())

    def _mysql_columns(
        self,
        cursor: Any,
        database: str,
    ) -> dict[tuple[str, str], list[SchemaColumn]]:
        cursor.execute(
            """
            SELECT table_schema, table_name, column_name, data_type, is_nullable,
                   ordinal_position, column_default
            FROM information_schema.columns
            WHERE table_schema = %s
            ORDER BY table_schema, table_name, ordinal_position
            """,
            (database,),
        )
        columns: dict[tuple[str, str], list[SchemaColumn]] = defaultdict(list)
        for row in cursor.fetchall():
            columns[(row["table_schema"], row["table_name"])].append(
                SchemaColumn(
                    name=row["column_name"],
                    data_type=row["data_type"],
                    nullable=row["is_nullable"] == "YES",
                    ordinal_position=row["ordinal_position"],
                    default=row["column_default"],
                )
            )
        return dict(columns)

    def _mysql_primary_keys(self, cursor: Any, database: str) -> dict[tuple[str, str], list[str]]:
        cursor.execute(
            """
            SELECT table_schema, table_name, column_name
            FROM information_schema.key_column_usage
            WHERE table_schema = %s AND constraint_name = 'PRIMARY'
            ORDER BY table_schema, table_name, ordinal_position
            """,
            (database,),
        )
        keys: dict[tuple[str, str], list[str]] = defaultdict(list)
        for row in cursor.fetchall():
            keys[(row["table_schema"], row["table_name"])].append(row["column_name"])
        return dict(keys)

    def _mysql_unique_identities(
        self,
        cursor: Any,
        database: str,
    ) -> dict[tuple[str, str], list[list[str]]]:
        cursor.execute(
            """
            SELECT table_schema, table_name, constraint_name, column_name
            FROM information_schema.key_column_usage
            WHERE table_schema = %s AND constraint_name != 'PRIMARY'
            ORDER BY table_schema, table_name, constraint_name, ordinal_position
            """,
            (database,),
        )
        grouped: dict[tuple[str, str, str], list[str]] = defaultdict(list)
        for row in cursor.fetchall():
            grouped[(row["table_schema"], row["table_name"], row["constraint_name"])].append(
                row["column_name"]
            )
        identities: dict[tuple[str, str], list[list[str]]] = defaultdict(list)
        for (schema_name, table_name, _), columns in grouped.items():
            identities[(schema_name, table_name)].append(columns)
        return dict(identities)

    def _mysql_indexes(
        self, cursor: Any, database: str
    ) -> dict[tuple[str, str], list[SchemaIndex]]:
        cursor.execute(
            """
            SELECT table_schema, table_name, index_name, column_name, non_unique
            FROM information_schema.statistics
            WHERE table_schema = %s
            ORDER BY table_schema, table_name, index_name, seq_in_index
            """,
            (database,),
        )
        grouped: dict[tuple[str, str, str], dict[str, Any]] = {}
        for row in cursor.fetchall():
            key = (row["table_schema"], row["table_name"], row["index_name"])
            index = grouped.setdefault(
                key,
                {"columns": [], "unique": row["non_unique"] == 0},
            )
            index["columns"].append(row["column_name"])
        indexes: dict[tuple[str, str], list[SchemaIndex]] = defaultdict(list)
        for (schema_name, table_name, index_name), data in grouped.items():
            indexes[(schema_name, table_name)].append(
                SchemaIndex(name=index_name, columns=data["columns"], unique=data["unique"])
            )
        return dict(indexes)

    def _mysql_relationships(
        self,
        cursor: Any,
        database: str,
    ) -> dict[tuple[str, str], list[SchemaRelationship]]:
        cursor.execute(
            """
            SELECT table_schema, table_name, constraint_name, column_name,
                   referenced_table_schema AS referenced_schema,
                   referenced_table_name AS referenced_table,
                   referenced_column_name AS referenced_column
            FROM information_schema.key_column_usage
            WHERE table_schema = %s AND referenced_table_name IS NOT NULL
            ORDER BY table_schema, table_name, constraint_name, ordinal_position
            """,
            (database,),
        )
        rows = [
            (
                row["table_schema"],
                row["table_name"],
                row["constraint_name"],
                row["column_name"],
                row["referenced_schema"],
                row["referenced_table"],
                row["referenced_column"],
            )
            for row in cursor.fetchall()
        ]
        return self._relationships_from_rows(rows)

    def _relationships_from_rows(
        self,
        rows: list[tuple[str, str, str, str, str, str, str]],
    ) -> dict[tuple[str, str], list[SchemaRelationship]]:
        grouped: dict[tuple[str, str, str, str, str], dict[str, list[str]]] = {}
        for row in rows:
            key = (row[0], row[1], row[2], row[4], row[5])
            relationship = grouped.setdefault(key, {"columns": [], "referenced_columns": []})
            relationship["columns"].append(row[3])
            relationship["referenced_columns"].append(row[6])
        relationships: dict[tuple[str, str], list[SchemaRelationship]] = defaultdict(list)
        for (
            schema_name,
            table_name,
            constraint_name,
            referenced_schema,
            referenced_table,
        ), data in grouped.items():
            relationships[(schema_name, table_name)].append(
                SchemaRelationship(
                    name=constraint_name,
                    columns=data["columns"],
                    referenced_schema=referenced_schema,
                    referenced_table=referenced_table,
                    referenced_columns=data["referenced_columns"],
                )
            )
        return dict(relationships)
