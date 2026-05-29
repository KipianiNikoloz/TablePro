## Why

TablePro can now authenticate a local admin, store saved direct database connections, and test connectivity. The next backend dependency is schema introspection so users can browse database structure and later query, edit, import, and AI workflows can reason about tables, keys, and relationships.

## What Changes

- Add schema snapshot persistence for saved connections.
- Add schema domain models for tables, columns, indexes, primary keys, unique identities, and relationships.
- Add a dialect introspection boundary with Postgres and MySQL implementations.
- Add authenticated schema cache and manual refresh APIs for saved connections.
- Keep query execution, pane sessions, inline edits, CSV, frontend UI, and automatic invalidation deferred.

## Capabilities

### New Capabilities

- `tablepro-schema-introspection`: Defines cached schema snapshots and manual refresh behavior for saved database connections.

### Modified Capabilities

- None.

## Impact

- Adds a SQLite app database migration for schema snapshots.
- Adds backend service, repository, port, adapter, API schema, routes, and tests.
- Uses existing saved connection credential resolution server-side.
- Does not expose credentials, connection strings, secret refs, or query result data to browser code.
