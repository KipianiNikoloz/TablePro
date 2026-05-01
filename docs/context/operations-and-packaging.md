# Operations and Packaging Context

## Packaging

V1 ships as a Docker image. Production runtime should be a single container with FastAPI serving static Next.js assets and backend APIs.

## Persistent Volume

Use a mounted local volume for the SQLite app database and encrypted secrets. The volume stores:

- saved connection metadata
- encrypted secret material
- workspaces and pane state
- query history metadata
- bookmarks
- schema cache
- AI provider config
- audit records
- migration state

Do not persist query result data by default.

## Startup and Unlock

On startup:

1. Run SQLite app migrations.
2. Start locked if encrypted secrets exist.
3. Serve login/unlock UI.
4. Unlock vault after successful admin passphrase login.

## Backup and Restore

V1 should provide encrypted volume export/import for app config, history, bookmarks, connection metadata, and encrypted secret data. Restored volumes still require the admin passphrase.

## Resource Limits

Use conservative defaults:

- query timeout
- row limit
- idle pane-session timeout
- max concurrent jobs
- max export size
- temp result store size
- upload/import size limit

Provide visible override controls where appropriate, but defaults should protect the browser, backend, and target database.

## Migrations

Use explicit versioned migrations for the SQLite app database. Startup migrations should fail safely and should not silently discard user state.

## Observability

Prefer structured logs with redaction. Logs should be useful for local debugging without exposing secrets or database row data by default.
