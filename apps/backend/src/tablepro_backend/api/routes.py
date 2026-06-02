from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, Response, status

from tablepro_backend.api.schemas import (
    AuthActionResponse,
    AuthStatusResponse,
    ConnectionCreateRequest,
    ConnectionListResponse,
    ConnectionResponse,
    ConnectionTestRequestBody,
    ConnectionTestResponse,
    ConnectionUpdateRequest,
    HealthResponse,
    PassphraseRequest,
    QueryColumnResponse,
    QueryErrorResponse,
    QueryJobResponse,
    QueryResultPageResponse,
    QuerySubmitRequest,
    ReadinessResponse,
    RuntimeResponse,
    SchemaCacheMissResponse,
    SchemaColumnResponse,
    SchemaIndexResponse,
    SchemaRelationshipResponse,
    SchemaResponse,
    SchemaSnapshotResponse,
    SchemaTableResponse,
)
from tablepro_backend.application.services.auth import AuthService, AuthStatus
from tablepro_backend.application.services.connections import ConnectionService
from tablepro_backend.application.services.runtime_status import (
    build_readiness,
    build_runtime_info,
)
from tablepro_backend.application.services.schema import SchemaService
from tablepro_backend.application.services.query import QueryService
from tablepro_backend.core.config import Settings
from tablepro_backend.domain.auth import (
    InvalidPassphraseError,
    SecretRefNotFoundError,
    SessionInvalidError,
    VaultLockedError,
    VaultAlreadyInitializedError,
    VaultNotInitializedError,
)
from tablepro_backend.domain.connections import (
    ConnectionInput,
    ConnectionNotFoundError,
    ConnectionTestRequest,
    ConnectionTestResult,
    ConnectionUpdate,
    ConnectionValidationError,
    SavedConnection,
)
from tablepro_backend.domain.schema import (
    SchemaRefreshError,
    SchemaSnapshot,
    SchemaSnapshotNotFoundError,
)
from tablepro_backend.domain.query import (
    QueryJob,
    QueryJobNotFoundError,
    QueryResultNotFoundError,
    QueryResultPage,
    QuerySubmit,
    QueryValidationError,
)

router = APIRouter()


def _settings(request: Request) -> Settings:
    return request.app.state.settings


def _auth_service(request: Request) -> AuthService:
    return request.app.state.auth_service


def _connection_service(request: Request) -> ConnectionService:
    return request.app.state.connection_service


def _schema_service(request: Request) -> SchemaService:
    return request.app.state.schema_service


def _query_service(request: Request) -> QueryService:
    return request.app.state.query_service


def _session_cookie(request: Request) -> str | None:
    return request.cookies.get(_settings(request).auth_cookie_name)


def _auth_response(auth_status: AuthStatus) -> AuthActionResponse:
    return AuthActionResponse(
        initialized=auth_status.initialized,
        authenticated=auth_status.authenticated,
        vault_unlocked=auth_status.vault_unlocked,
        setup_required=auth_status.setup_required,
    )


def _set_session_cookie(response: Response, settings: Settings, token: str) -> None:
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=token,
        max_age=settings.auth_session_idle_timeout_seconds,
        httponly=True,
        secure=settings.auth_session_cookie_secure,
        samesite=settings.auth_session_cookie_samesite,
    )


def _clear_session_cookie(response: Response, settings: Settings) -> None:
    response.delete_cookie(
        key=settings.auth_cookie_name,
        httponly=True,
        secure=settings.auth_session_cookie_secure,
        samesite=settings.auth_session_cookie_samesite,
    )


def _require_auth(request: Request) -> None:
    try:
        _auth_service(request).require_session(_session_cookie(request))
    except SessionInvalidError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


def _connection_response(connection: SavedConnection) -> ConnectionResponse:
    return ConnectionResponse(
        id=connection.id,
        name=connection.name,
        dialect=connection.dialect,
        host=connection.host,
        port=connection.port,
        database=connection.database,
        username=connection.username,
        environment_label=connection.environment_label,
        has_password=connection.has_password,
        created_at=connection.created_at.isoformat(),
        updated_at=connection.updated_at.isoformat(),
    )


def _test_response(result: ConnectionTestResult) -> ConnectionTestResponse:
    return ConnectionTestResponse(ok=result.ok, dialect=result.dialect, message=result.message)


def _schema_response(snapshot: SchemaSnapshot) -> SchemaSnapshotResponse:
    return SchemaSnapshotResponse(
        connection_id=snapshot.connection_id,
        dialect=snapshot.dialect,
        refreshed_at=snapshot.refreshed_at.isoformat(),
        tables=[
            SchemaTableResponse(
                schema_name=table.schema_name,
                name=table.name,
                columns=[
                    SchemaColumnResponse(
                        name=column.name,
                        data_type=column.data_type,
                        nullable=column.nullable,
                        ordinal_position=column.ordinal_position,
                        default=column.default,
                    )
                    for column in table.columns
                ],
                primary_key=table.primary_key,
                unique_identities=table.unique_identities,
                indexes=[
                    SchemaIndexResponse(
                        name=index.name,
                        columns=index.columns,
                        unique=index.unique,
                    )
                    for index in table.indexes
                ],
                relationships=[
                    SchemaRelationshipResponse(
                        name=relationship.name,
                        columns=relationship.columns,
                        referenced_schema=relationship.referenced_schema,
                        referenced_table=relationship.referenced_table,
                        referenced_columns=relationship.referenced_columns,
                    )
                    for relationship in table.relationships
                ],
            )
            for table in snapshot.tables
        ],
    )


def _query_job_response(job: QueryJob) -> QueryJobResponse:
    return QueryJobResponse(
        id=job.id,
        connection_id=job.connection_id,
        pane_id=job.pane_id,
        status=job.status,
        submitted_at=job.submitted_at.isoformat(),
        started_at=job.started_at.isoformat() if job.started_at else None,
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        duration_ms=job.duration_ms,
        row_count=job.row_count,
        rows_affected=job.rows_affected,
        has_result=job.result_handle is not None,
        page_size=job.page_size,
        total_rows=job.total_rows,
        limit_reached=job.limit_reached,
        transaction_state=job.transaction_state,
        error=(
            QueryErrorResponse(
                code=job.error.code,
                message=job.error.message,
                category=job.error.category,
            )
            if job.error
            else None
        ),
    )


def _query_page_response(page: QueryResultPage) -> QueryResultPageResponse:
    return QueryResultPageResponse(
        job_id=page.job_id,
        page_index=page.page_index,
        page_size=page.page_size,
        total_rows=page.total_rows,
        columns=[
            QueryColumnResponse(name=column.name, data_type=column.data_type)
            for column in page.columns
        ],
        rows=page.rows,
        limit_reached=page.limit_reached,
    )


def _connection_error(exc: Exception) -> HTTPException:
    if isinstance(exc, ConnectionNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, (VaultLockedError, SecretRefNotFoundError)):
        return HTTPException(
            status_code=status.HTTP_423_LOCKED, detail="Vault is locked or unavailable."
        )
    if isinstance(exc, ConnectionValidationError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Connection operation failed."
    )


def _schema_error(exc: Exception) -> HTTPException:
    if isinstance(exc, ConnectionNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, VaultLockedError):
        return HTTPException(status_code=status.HTTP_423_LOCKED, detail="Vault is locked.")
    if isinstance(exc, SchemaRefreshError):
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="Schema refresh failed."
        )
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Schema operation failed.")


def _query_error(exc: Exception) -> HTTPException:
    if isinstance(exc, (QueryJobNotFoundError, QueryResultNotFoundError)):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, ConnectionNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, VaultLockedError):
        return HTTPException(status_code=status.HTTP_423_LOCKED, detail="Vault is locked.")
    if isinstance(exc, (ConnectionValidationError, QueryValidationError)):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query operation failed.")


@router.get("/healthz", response_model=HealthResponse)
def healthz() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/readyz", response_model=ReadinessResponse)
def readyz(request: Request) -> ReadinessResponse:
    return build_readiness(_settings(request))


@router.get("/api/runtime", response_model=RuntimeResponse)
def runtime(request: Request) -> RuntimeResponse:
    vault_status = _auth_service(request).vault.status().status
    return build_runtime_info(_settings(request), vault_status)


@router.get("/api/auth/status", response_model=AuthStatusResponse)
def auth_status(request: Request) -> AuthStatusResponse:
    service = _auth_service(request)
    return _auth_response(service.status(_session_cookie(request)))


@router.post("/api/auth/setup", response_model=AuthActionResponse)
def setup_auth(request: Request, response: Response, body: PassphraseRequest) -> AuthActionResponse:
    service = _auth_service(request)
    try:
        session = service.setup(body.passphrase)
    except VaultAlreadyInitializedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except InvalidPassphraseError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    _set_session_cookie(response, _settings(request), session.token)
    return _auth_response(service.status(session.token))


@router.post("/api/auth/login", response_model=AuthActionResponse)
def login(request: Request, response: Response, body: PassphraseRequest) -> AuthActionResponse:
    service = _auth_service(request)
    try:
        session = service.login(body.passphrase)
    except VaultNotInitializedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except InvalidPassphraseError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid passphrase."
        ) from exc
    _set_session_cookie(response, _settings(request), session.token)
    return _auth_response(service.status(session.token))


@router.post("/api/auth/logout", response_model=AuthActionResponse)
def logout(request: Request, response: Response) -> AuthActionResponse:
    service = _auth_service(request)
    try:
        service.logout(_session_cookie(request))
    except SessionInvalidError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    _clear_session_cookie(response, _settings(request))
    return _auth_response(service.status(None))


@router.post("/api/auth/lock", response_model=AuthActionResponse)
def lock(request: Request, response: Response) -> AuthActionResponse:
    service = _auth_service(request)
    try:
        service.lock(_session_cookie(request))
    except SessionInvalidError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    _clear_session_cookie(response, _settings(request))
    return _auth_response(service.status(None))


@router.get("/api/connections", response_model=ConnectionListResponse)
def list_connections(request: Request) -> ConnectionListResponse:
    _require_auth(request)
    connections = _connection_service(request).list()
    return ConnectionListResponse(connections=[_connection_response(item) for item in connections])


@router.post("/api/connections", response_model=ConnectionResponse)
def create_connection(request: Request, body: ConnectionCreateRequest) -> ConnectionResponse:
    _require_auth(request)
    try:
        connection = _connection_service(request).create(
            ConnectionInput(
                name=body.name,
                dialect=body.dialect,
                host=body.host,
                port=body.port,
                database=body.database,
                username=body.username,
                password=body.password,
                environment_label=body.environment_label,
            )
        )
    except Exception as exc:
        raise _connection_error(exc) from exc
    return _connection_response(connection)


@router.get("/api/connections/{connection_id}", response_model=ConnectionResponse)
def get_connection(request: Request, connection_id: str) -> ConnectionResponse:
    _require_auth(request)
    try:
        connection = _connection_service(request).get(connection_id)
    except Exception as exc:
        raise _connection_error(exc) from exc
    return _connection_response(connection)


@router.patch("/api/connections/{connection_id}", response_model=ConnectionResponse)
def update_connection(
    request: Request,
    connection_id: str,
    body: ConnectionUpdateRequest,
) -> ConnectionResponse:
    _require_auth(request)
    try:
        connection = _connection_service(request).update(
            connection_id,
            ConnectionUpdate(
                name=body.name,
                host=body.host,
                port=body.port,
                database=body.database,
                username=body.username,
                password=body.password,
                environment_label=body.environment_label,
            ),
        )
    except Exception as exc:
        raise _connection_error(exc) from exc
    return _connection_response(connection)


@router.delete("/api/connections/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_connection(request: Request, connection_id: str) -> Response:
    _require_auth(request)
    try:
        _connection_service(request).delete(connection_id)
    except Exception as exc:
        raise _connection_error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/api/connections/test", response_model=ConnectionTestResponse)
def test_provided_connection(
    request: Request,
    body: ConnectionTestRequestBody,
) -> ConnectionTestResponse:
    _require_auth(request)
    try:
        result = _connection_service(request).test_provided(
            ConnectionTestRequest(
                dialect=body.dialect,
                host=body.host,
                port=body.port,
                database=body.database,
                username=body.username,
                password=body.password,
            )
        )
    except Exception as exc:
        raise _connection_error(exc) from exc
    return _test_response(result)


@router.post("/api/connections/{connection_id}/test", response_model=ConnectionTestResponse)
def test_saved_connection(request: Request, connection_id: str) -> ConnectionTestResponse:
    _require_auth(request)
    try:
        result = _connection_service(request).test_saved(connection_id)
    except Exception as exc:
        raise _connection_error(exc) from exc
    return _test_response(result)


@router.get(
    "/api/connections/{connection_id}/schema",
    response_model=SchemaResponse | SchemaCacheMissResponse,
)
def get_connection_schema(
    request: Request, connection_id: str
) -> SchemaResponse | SchemaCacheMissResponse:
    _require_auth(request)
    try:
        snapshot = _schema_service(request).get_cached(connection_id)
    except SchemaSnapshotNotFoundError:
        return SchemaCacheMissResponse(message="Schema snapshot has not been refreshed yet.")
    except Exception as exc:
        raise _schema_error(exc) from exc
    return SchemaResponse(status="ready", snapshot=_schema_response(snapshot))


@router.post("/api/connections/{connection_id}/schema/refresh", response_model=SchemaResponse)
def refresh_connection_schema(request: Request, connection_id: str) -> SchemaResponse:
    _require_auth(request)
    try:
        snapshot = _schema_service(request).refresh(connection_id)
    except Exception as exc:
        raise _schema_error(exc) from exc
    return SchemaResponse(status="ready", snapshot=_schema_response(snapshot))


@router.post("/api/query/jobs", response_model=QueryJobResponse)
def submit_query(request: Request, body: QuerySubmitRequest) -> QueryJobResponse:
    _require_auth(request)
    try:
        job = _query_service(request).submit(
            QuerySubmit(
                connection_id=body.connection_id,
                pane_id=body.pane_id,
                sql=body.sql,
                page_size=body.page_size,
                row_limit=body.row_limit,
            )
        )
    except Exception as exc:
        raise _query_error(exc) from exc
    return _query_job_response(job)


@router.get("/api/query/jobs/{job_id}", response_model=QueryJobResponse)
def get_query_job(request: Request, job_id: str) -> QueryJobResponse:
    _require_auth(request)
    try:
        job = _query_service(request).get(job_id)
    except Exception as exc:
        raise _query_error(exc) from exc
    return _query_job_response(job)


@router.post("/api/query/jobs/{job_id}/cancel", response_model=QueryJobResponse)
def cancel_query_job(request: Request, job_id: str) -> QueryJobResponse:
    _require_auth(request)
    try:
        job = _query_service(request).cancel(job_id)
    except Exception as exc:
        raise _query_error(exc) from exc
    return _query_job_response(job)


@router.get("/api/query/jobs/{job_id}/pages/{page_index}", response_model=QueryResultPageResponse)
def get_query_result_page(
    request: Request,
    job_id: str,
    page_index: int,
) -> QueryResultPageResponse:
    _require_auth(request)
    try:
        page = _query_service(request).page(job_id, page_index)
    except Exception as exc:
        raise _query_error(exc) from exc
    return _query_page_response(page)
