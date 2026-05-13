## Context

The backend already has local admin setup, HTTP-only sessions, in-memory vault unlock state, and encrypted secret refs. Connection management should be the first feature to consume that trust boundary: browser code sends credentials when creating or testing a connection, but the backend owns persistence, vault encryption, and all future use of database credentials.

## Goals / Non-Goals

**Goals:**

- Persist direct Postgres/MySQL connection metadata in the app SQLite database.
- Store saved passwords as encrypted vault secret refs.
- Require a valid authenticated session and unlocked vault for saved connection mutations and tests that need credentials.
- Return connection metadata without raw passwords, encrypted blobs, or decrypted secret values.
- Provide minimal connectivity testing for direct Postgres/MySQL connections.

**Non-Goals:**

- Do not run arbitrary SQL, introspect schemas, create pane sessions, cache schemas, or manage result pages.
- Do not add frontend UI.
- Do not add SSH/cloud transports, connection pooling for query sessions, or import/export flows.
- Do not expose generic secret-ref CRUD over HTTP.

## Decisions

### Decision: Store password secret refs internally

Connection records store a password secret-ref id, while public API responses expose only whether a password is saved. This lets later query/session services resolve credentials server-side without making secret refs part of the browser contract.

### Decision: Require unlocked vault for connection writes and saved tests

Creating a saved connection, replacing a saved password, deleting a saved password, deleting a connection, and testing a saved connection may need secret-ref access. These operations require an authenticated session and unlocked vault. Read-only connection listing/getting requires authentication but does not need vault unlock.

### Decision: Test connectivity without query workflow scope

The driver adapter boundary only opens a connection and performs a tiny driver-native validation. It returns structured success/failure metadata and does not store result data, manage pane sessions, or execute user SQL.

## Risks / Trade-offs

- Installing native database drivers adds dependency surface. Keep driver use behind a small `ConnectionTester` boundary so tests can use fakes and future query adapters can evolve separately.
- Public validation errors can accidentally echo credentials. API and service errors must not include passwords, secret refs, or raw connection strings.
- Updating passwords needs careful cleanup. Replacing or deleting a saved password should remove the old secret ref after the metadata update succeeds.

## Migration Plan

1. Add a migration for `database_connections`.
2. Add domain types, repository behavior, service logic, and driver test ports.
3. Add connection API schemas/routes with auth guards.
4. Wire the service into FastAPI app state.
5. Add migration, service, API, and driver fake tests.

Rollback before users save connections can drop the migration and code. After users save connections, rollback requires deleting local app state or a future export path.

## Open Questions

- None for this slice.
