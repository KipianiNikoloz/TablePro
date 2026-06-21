# TablePro

TablePro is a local-first, Docker-targeted browser database manager for solo developers. It aims to provide a fast database cockpit accessible from a browser without installing a desktop app.

## Implementation Status

Only the **backend** (`apps/backend/`) is under active development. The Docker image, frontend, static file serving, and several product capabilities listed under V1 scope are still future / deferred work. See [product scope](docs/context/product.md) for the full V1 plan.

## Repository Layout

- `apps/backend/` — FastAPI backend (Python) with local auth/vault, saved connections, schema introspection, and backend-owned query execution.
- `docs/context/` — Architecture, design, security, and operations context shards (`*.md`).
- `openspec/` — OpenSpec product and architecture intent documents.
- `.github/workflows/` — CI, security, and release-scaffold workflow definitions.
- `static/tablepro_design_deck.pdf` — Visual design reference for the future frontend.

## Backend Local Development

Commands below assume `uv` is installed. Run them from the `apps/backend/` directory.

```powershell
uv sync
uv run pytest
uv run uvicorn tablepro_backend.main:app --reload
```

The backend reads settings from environment variables prefixed with `TABLEPRO_`. Key settings include `TABLEPRO_DATA_DIR`, `TABLEPRO_SQLITE_PATH`, `TABLEPRO_LOG_LEVEL`, `TABLEPRO_AUTH_SESSION_IDLE_TIMEOUT_SECONDS`, and `TABLEPRO_AUTH_SESSION_COOKIE_SECURE`.

## Quality and Security Checks

Run these from `apps/backend/` to verify code quality and dependencies:

```powershell
uv lock --check
uv sync --frozen --all-groups
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run pip-audit
uv run bandit -r src
```

> **Note:** `pip-audit` may report `tablepro-backend` as "not found on PyPI". This is expected because `tablepro-backend` is the local editable project package, not a published package. Actionable vulnerability findings come from third-party dependency entries.

## Product and Architecture Intent

- [docs/context/product.md](docs/context/product.md) — V1 scope, user, non-goals, and product bias.
- [docs/context/system-architecture.md](docs/context/system-architecture.md) — Runtime topology, trust boundaries, and system flow.
- [docs/context/backend.md](docs/context/backend.md) — Stack, hexagonal architecture, services, and domain concepts.
- [docs/context/database-workflows.md](docs/context/database-workflows.md) — Connections, schema, queries, edits, imports, exports.
- [docs/context/security-and-safety.md](docs/context/security-and-safety.md) — Auth, vault, production safety, and logging privacy.
- [docs/context/operations-and-packaging.md](docs/context/operations-and-packaging.md) — Docker packaging, volumes, migrations, and resource limits.
- `openspec/` — Source-of-truth product and architecture documents.
