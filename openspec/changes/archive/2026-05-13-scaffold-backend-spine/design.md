## Context

The repository is moving from architecture-only context to the first runnable code. The backend spine should prove the service shape, configuration, migrations, and status checks without designing product workflows before their dedicated changes.

## Decisions

### Decision: Use `apps/backend`

Place the FastAPI service in `apps/backend` so the repository can later add `apps/frontend` and packaging without reshuffling the first code.

### Decision: Use `uv` with `pyproject.toml`

Use a modern Python project file and `uv` commands for dependency management, test execution, and local development. This keeps Docker and CI setup repeatable later while remaining simple now.

### Decision: Use Alembic immediately

Initialize Alembic for the SQLite app database with a minimal initial migration. Startup should verify or apply migrations against the configured local app database and fail visibly if migration state cannot be established.

### Decision: Keep status APIs narrow

Expose only:

- `GET /healthz` for process liveness.
- `GET /readyz` for app database/migration readiness.
- `GET /api/runtime` for redacted runtime metadata useful to the browser and local debugging.

These endpoints should not expose raw paths that include secrets, credentials, connection strings, or vault material.

### Decision: Prepare but do not implement auth/vault

Add small boundary types or service shells for vault readiness and secret redaction, but do not implement login, passphrase handling, encryption, saved connection credentials, or unlock flows in this change.

## Risks / Trade-offs

- Applying migrations at startup can hide migration design details too early -> keep the migration runner minimal and SQLite-only for the app database.
- Health/status endpoints can become product APIs by accident -> keep them explicitly operational and avoid workflow data.
- Placeholder auth/vault code can become fake security -> make it clear in names and tests that the real unlock/encryption behavior is deferred.

## Deferred Scope

- Frontend and shadcn initialization.
- Production Docker packaging and static Next.js serving.
- Real local admin login, vault encryption, and saved credentials.
- Postgres/MySQL dialect adapters, connection tests, query jobs, result paging, WebSockets, imports, exports, and AI provider behavior.
