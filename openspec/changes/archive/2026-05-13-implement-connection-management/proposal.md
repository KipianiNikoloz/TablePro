## Why

TablePro can now start, initialize a local admin vault, authenticate a browser, and store encrypted internal secret refs. The next product dependency is saved database connections, because schema browsing, query execution, imports, exports, workspaces, and AI drafting all need a safe connection model before they can be useful.

## What Changes

- Add backend support for saved direct Postgres and MySQL connection metadata.
- Store connection passwords through the existing vault secret-ref boundary.
- Add authenticated connection APIs for create, list, get, update, delete, and connectivity testing.
- Add minimal database driver adapters for testing connectivity only.
- Keep query execution, schema introspection, pane sessions, frontend UI, CSV, and AI workflows deferred.

## Capabilities

### New Capabilities

- `tablepro-connection-management`: Defines saved direct database connections, credential-safe API responses, vault-backed password storage, and connection test behavior.

### Modified Capabilities

- None.

## Impact

- Adds a SQLite app database migration for connection records.
- Adds backend service, repository, port, adapter, API schema, route, and tests for connection management.
- Adds Postgres/MySQL driver dependencies needed only for connectivity checks.
- Does not expose raw database credentials or generic browser-facing secret APIs.
