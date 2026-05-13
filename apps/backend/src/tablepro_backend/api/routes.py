from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, Response, status

from tablepro_backend.api.schemas import (
    AuthActionResponse,
    AuthStatusResponse,
    HealthResponse,
    PassphraseRequest,
    ReadinessResponse,
    RuntimeResponse,
)
from tablepro_backend.application.services.auth import AuthService, AuthStatus
from tablepro_backend.application.services.runtime_status import (
    build_readiness,
    build_runtime_info,
)
from tablepro_backend.core.config import Settings
from tablepro_backend.domain.auth import (
    InvalidPassphraseError,
    SessionInvalidError,
    VaultAlreadyInitializedError,
    VaultNotInitializedError,
)

router = APIRouter()


def _settings(request: Request) -> Settings:
    return request.app.state.settings


def _auth_service(request: Request) -> AuthService:
    return request.app.state.auth_service


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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid passphrase.") from exc
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
