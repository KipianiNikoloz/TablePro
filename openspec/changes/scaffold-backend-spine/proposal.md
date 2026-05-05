## Why

TablePro currently has durable architecture and UI context but no runnable application code. The first implementation chunk should establish a small backend spine so future workflow work has a real FastAPI service, app database migration layer, and test harness to build on.

## What Changes

- Scaffold a backend service under `apps/backend`.
- Add a `uv`/`pyproject.toml` Python project with FastAPI, pytest, and Alembic.
- Add a minimal FastAPI app with health, readiness, and redacted runtime status endpoints.
- Add settings, logging, startup migration checks, and a SQLite app database migration baseline.
- Add placeholder auth/vault boundary types without implementing passphrase login, encryption, saved credentials, database connections, query execution, WebSockets, frontend code, or Docker packaging.

## Capabilities

### New Capabilities

- `tablepro-backend-spine`: Defines the runnable FastAPI backend foundation, local app database migration baseline, status APIs, redacted runtime metadata, and placeholder vault boundary.

### Modified Capabilities

- None.

## Impact

- Adds `apps/backend` runtime and test code.
- Adds backend Python dependencies and local development commands.
- Adds a new OpenSpec capability for the first implementation foundation.
- Does not change product workflow scope or approve deferred database, vault, frontend, or packaging behavior.
