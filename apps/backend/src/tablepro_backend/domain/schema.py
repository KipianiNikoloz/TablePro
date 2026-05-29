from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from tablepro_backend.domain.connections import ConnectionDialect


class SchemaError(Exception):
    """Base class for schema introspection errors."""


class SchemaSnapshotNotFoundError(SchemaError):
    """Raised when no cached schema snapshot exists."""


class SchemaRefreshError(SchemaError):
    """Raised when target database schema refresh fails."""


@dataclass(frozen=True)
class SchemaColumn:
    name: str
    data_type: str
    nullable: bool
    ordinal_position: int
    default: str | None = None


@dataclass(frozen=True)
class SchemaIndex:
    name: str
    columns: list[str]
    unique: bool


@dataclass(frozen=True)
class SchemaRelationship:
    name: str
    columns: list[str]
    referenced_schema: str
    referenced_table: str
    referenced_columns: list[str]


@dataclass(frozen=True)
class SchemaTable:
    schema_name: str
    name: str
    columns: list[SchemaColumn]
    primary_key: list[str] = field(default_factory=list)
    unique_identities: list[list[str]] = field(default_factory=list)
    indexes: list[SchemaIndex] = field(default_factory=list)
    relationships: list[SchemaRelationship] = field(default_factory=list)


@dataclass(frozen=True)
class SchemaSnapshot:
    connection_id: str
    dialect: ConnectionDialect
    refreshed_at: datetime
    tables: list[SchemaTable]


@dataclass(frozen=True)
class SchemaIntrospectionRequest:
    connection_id: str
    dialect: ConnectionDialect
    host: str
    port: int
    database: str
    username: str
    password: str
