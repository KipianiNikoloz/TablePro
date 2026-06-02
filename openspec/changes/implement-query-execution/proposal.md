## Why

TablePro can authenticate a local admin, store saved connections, and refresh schema metadata. The next product dependency is backend-owned query execution so the browser can run SQL without receiving database credentials and future editor, grid, history, edit, export, import, and AI workflows have a job/result foundation.

## What Changes

- Add authenticated backend query submission for saved Postgres/MySQL connections.
- Add pane-scoped database sessions so explicit transaction state belongs to the pane that ran the SQL.
- Add query jobs with status, timing, row counts, structured errors, cancellation, and resource-limit metadata.
- Add temporary paged result storage and result-page APIs.
- Add driver-backed query adapters for Postgres and MySQL behind a query execution port.
- Keep frontend UI, WebSocket events, query history/bookmarks, inline edits, CSV import/export, AI drafting, and durable result storage deferred.

## Capabilities

### New Capabilities

- `tablepro-query-execution`: Defines backend-owned query submission, pane sessions, query jobs, cancellation, and paged result access for saved database connections.

### Modified Capabilities

- None.

## Impact

- Adds backend domain models, ports, service, infrastructure adapters, API schemas/routes, settings, and tests.
- Uses existing saved connection and vault services to resolve credentials server-side.
- Adds no browser-facing credential, secret-ref, connection-string, or durable result-data exposure.
