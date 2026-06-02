from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from pydantic import Field
from typing import Literal


class HealthResponse(BaseModel):
    status: str


class ReadinessCheck(BaseModel):
    name: str
    status: str
    message: str
    details: dict[str, str | bool | None] = Field(default_factory=dict)


class ReadinessResponse(BaseModel):
    status: str
    checks: list[ReadinessCheck]


class PassphraseRequest(BaseModel):
    passphrase: str = Field(min_length=1)


class AuthStatusResponse(BaseModel):
    initialized: bool
    authenticated: bool
    vault_unlocked: bool
    setup_required: bool


class AuthActionResponse(BaseModel):
    initialized: bool
    authenticated: bool
    vault_unlocked: bool
    setup_required: bool


class RuntimeResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    app_name: str
    app_version: str
    environment: str
    data_dir_configured: bool
    sqlite_configured: bool
    migrations_on_startup: bool
    vault_status: str
    deferred_capabilities: list[str]


ConnectionDialect = Literal["postgres", "mysql"]


class ConnectionCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    dialect: ConnectionDialect
    host: str = Field(min_length=1, max_length=255)
    port: int = Field(ge=1, le=65535)
    database: str = Field(min_length=1, max_length=255)
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1)
    environment_label: str = Field(min_length=1, max_length=40)


class ConnectionUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    host: str | None = Field(default=None, min_length=1, max_length=255)
    port: int | None = Field(default=None, ge=1, le=65535)
    database: str | None = Field(default=None, min_length=1, max_length=255)
    username: str | None = Field(default=None, min_length=1, max_length=255)
    password: str | None = Field(default=None, min_length=1)
    environment_label: str | None = Field(default=None, min_length=1, max_length=40)


class ConnectionResponse(BaseModel):
    id: str
    name: str
    dialect: ConnectionDialect
    host: str
    port: int
    database: str
    username: str
    environment_label: str
    has_password: bool
    created_at: str
    updated_at: str


class ConnectionListResponse(BaseModel):
    connections: list[ConnectionResponse]


class ConnectionTestRequestBody(BaseModel):
    dialect: ConnectionDialect
    host: str = Field(min_length=1, max_length=255)
    port: int = Field(ge=1, le=65535)
    database: str = Field(min_length=1, max_length=255)
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1)


class ConnectionTestResponse(BaseModel):
    ok: bool
    dialect: ConnectionDialect
    message: str


class SchemaColumnResponse(BaseModel):
    name: str
    data_type: str
    nullable: bool
    ordinal_position: int
    default: str | None = None


class SchemaIndexResponse(BaseModel):
    name: str
    columns: list[str]
    unique: bool


class SchemaRelationshipResponse(BaseModel):
    name: str
    columns: list[str]
    referenced_schema: str
    referenced_table: str
    referenced_columns: list[str]


class SchemaTableResponse(BaseModel):
    schema_name: str
    name: str
    columns: list[SchemaColumnResponse]
    primary_key: list[str]
    unique_identities: list[list[str]]
    indexes: list[SchemaIndexResponse]
    relationships: list[SchemaRelationshipResponse]


class SchemaSnapshotResponse(BaseModel):
    connection_id: str
    dialect: ConnectionDialect
    refreshed_at: str
    tables: list[SchemaTableResponse]


class SchemaCacheMissResponse(BaseModel):
    status: str = "missing"
    message: str


class SchemaResponse(BaseModel):
    status: str
    snapshot: SchemaSnapshotResponse | None = None
    message: str | None = None


class QuerySubmitRequest(BaseModel):
    connection_id: str = Field(min_length=1)
    pane_id: str = Field(min_length=1, max_length=160)
    sql: str = Field(min_length=1)
    page_size: int | None = Field(default=None, ge=1)
    row_limit: int | None = Field(default=None, ge=1)


class QueryErrorResponse(BaseModel):
    code: str
    message: str
    category: str


class QueryJobResponse(BaseModel):
    id: str
    connection_id: str
    pane_id: str
    status: str
    submitted_at: str
    started_at: str | None = None
    completed_at: str | None = None
    duration_ms: int | None = None
    row_count: int | None = None
    rows_affected: int | None = None
    has_result: bool
    page_size: int | None = None
    total_rows: int | None = None
    limit_reached: bool
    transaction_state: str
    error: QueryErrorResponse | None = None


class QueryColumnResponse(BaseModel):
    name: str
    data_type: str | None = None


class QueryResultPageResponse(BaseModel):
    job_id: str
    page_index: int
    page_size: int
    total_rows: int
    columns: list[QueryColumnResponse]
    rows: list[list[object]]
    limit_reached: bool
