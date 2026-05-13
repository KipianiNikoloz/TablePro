## 1. OpenSpec Validation

- [x] 1.1 Validate `implement-connection-management` before implementation.

## 2. Persistence and Dependencies

- [x] 2.1 Add driver dependencies and a SQLite migration for saved connection metadata.
- [x] 2.2 Add connection domain models/errors, repository behavior, and connectivity-test port types.

## 3. Connection Service and API

- [x] 3.1 Implement connection CRUD and vault-backed password handling.
- [x] 3.2 Implement Postgres/MySQL connectivity-test adapters.
- [x] 3.3 Add authenticated connection request/response schemas and API routes.
- [x] 3.4 Wire the connection service into FastAPI app state.

## 4. Verification

- [x] 4.1 Add migration tests for connection tables.
- [x] 4.2 Add service tests for CRUD, vault integration, redaction, and locked-vault failures.
- [x] 4.3 Add API tests for auth, validation, redaction, and connection test behavior using fakes.
- [x] 4.4 Run backend tests and OpenSpec validation.
- [x] 4.5 Review git status for intended files only.
