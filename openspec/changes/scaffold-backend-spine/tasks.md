## 1. OpenSpec Change

- [x] 1.1 Create proposal, design, capability spec, and tasks for `scaffold-backend-spine`.
- [x] 1.2 Validate the OpenSpec change before and after implementation.

## 2. Backend Project Scaffold

- [x] 2.1 Add `apps/backend` with `pyproject.toml`, package layout, test layout, and local `uv` commands.
- [x] 2.2 Add FastAPI application factory/entrypoint and basic structured logging setup.
- [x] 2.3 Add settings for app name/version, log level, local data directory, and SQLite app database path.

## 3. App Database and Readiness

- [x] 3.1 Add Alembic configuration and an initial SQLite app metadata migration.
- [x] 3.2 Add a startup migration runner and readiness checker for app database migration state.

## 4. Status APIs and Boundaries

- [x] 4.1 Add `GET /healthz`, `GET /readyz`, and `GET /api/runtime`.
- [x] 4.2 Add placeholder vault/auth boundary code that exposes no real credential behavior yet.
- [x] 4.3 Ensure status/runtime responses redact secret-like configuration and never expose raw credentials.

## 5. Verification

- [x] 5.1 Add tests for settings defaults, runtime redaction, API responses, and SQLite migration initialization.
- [x] 5.2 Run backend tests.
- [x] 5.3 Review git status for intended files only.
