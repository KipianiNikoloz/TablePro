from __future__ import annotations

from tablepro_backend.api.schemas import ReadinessCheck, ReadinessResponse, RuntimeResponse
from tablepro_backend.core.config import Settings
from tablepro_backend.infrastructure.database.readiness import check_app_database


def build_readiness(settings: Settings) -> ReadinessResponse:
    database_check = check_app_database(settings)
    checks = [
        ReadinessCheck(
            name="app_database",
            status="pass" if database_check.ready else "fail",
            message=database_check.message,
            details={
                "current_revision": database_check.current_revision,
                "head_revision": database_check.head_revision,
                "database_exists": database_check.database_exists,
            },
        )
    ]
    overall = "ready" if all(check.status == "pass" for check in checks) else "not_ready"
    return ReadinessResponse(status=overall, checks=checks)


def build_runtime_info(settings: Settings, vault_status: str) -> RuntimeResponse:
    return RuntimeResponse(
        app_name=settings.app_name,
        app_version=settings.app_version,
        environment=settings.environment,
        data_dir_configured=bool(settings.data_dir),
        sqlite_configured=bool(settings.sqlite_path),
        migrations_on_startup=settings.apply_migrations_on_startup,
        vault_status=vault_status,
        deferred_capabilities=[
            "schema_introspection",
            "query_execution",
        ],
    )
