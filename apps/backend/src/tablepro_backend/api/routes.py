from __future__ import annotations

from fastapi import APIRouter, Request

from tablepro_backend.api.schemas import HealthResponse, ReadinessResponse, RuntimeResponse
from tablepro_backend.application.services.runtime_status import (
    build_readiness,
    build_runtime_info,
)
from tablepro_backend.core.config import Settings

router = APIRouter()


def _settings(request: Request) -> Settings:
    return request.app.state.settings


@router.get("/healthz", response_model=HealthResponse)
def healthz() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/readyz", response_model=ReadinessResponse)
def readyz(request: Request) -> ReadinessResponse:
    return build_readiness(_settings(request))


@router.get("/api/runtime", response_model=RuntimeResponse)
def runtime(request: Request) -> RuntimeResponse:
    return build_runtime_info(_settings(request))
