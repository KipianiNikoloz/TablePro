## 1. OpenSpec Validation

- [x] 1.1 Validate `implement-schema-introspection` before implementation.

## 2. Persistence and Domain

- [x] 2.1 Add SQLite migration for latest schema snapshots per connection.
- [x] 2.2 Add schema domain models, errors, repository behavior, and introspection port types.

## 3. Service, Adapters, and API

- [x] 3.1 Implement schema cache lookup and manual refresh service behavior.
- [x] 3.2 Implement Postgres/MySQL schema introspection adapters.
- [x] 3.3 Add authenticated schema request/response schemas and routes.
- [x] 3.4 Wire schema service into FastAPI app state and runtime metadata.

## 4. Verification

- [x] 4.1 Add migration tests for schema snapshot storage.
- [x] 4.2 Add service tests for cache miss, refresh success, refresh failure preserving cache, locked vault, and redaction.
- [x] 4.3 Add API tests for auth, cache miss, refresh success, missing connection, locked vault, and secret-safe responses.
- [x] 4.4 Run Ruff, pytest, Bandit, pip-audit, and OpenSpec validation.
- [x] 4.5 Review git status for intended files only.
