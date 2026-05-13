from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from pydantic import Field


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
