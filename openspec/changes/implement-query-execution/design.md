## Context

The backend already owns local admin authentication, encrypted saved credentials, connection metadata, and cached schema snapshots. Query execution is the next backend boundary because browser code must submit SQL without receiving saved credentials, and later frontend/editor/grid features need a job and paging contract.

## Goals / Non-Goals

**Goals:**

- Run SQL against saved Postgres/MySQL connections through authenticated backend APIs.
- Keep saved credential resolution server-side and require an unlocked vault before query submission.
- Model each query as a job with status, timing, row counts, structured errors, cancellation, and result-page metadata.
- Use pane-scoped database sessions so explicit transactions are understandable and isolated by pane.
- Store result rows only in bounded temporary backend memory for this slice.

**Non-Goals:**

- Do not add frontend UI, WebSockets, history/bookmarks, inline edits, CSV import/export, AI drafting, or durable result persistence.
- Do not implement production destructive-query confirmation in this slice.
- Do not require live Postgres/MySQL services in the default test suite.

## Decisions

### Decision: In-process job manager for the first query slice

Query jobs are managed in process with a bounded worker pool. This matches the local-first single-container runtime and avoids adding premature SQLite job persistence before history/audit requirements are implemented.

### Decision: Temporary in-memory result store

Successful result-producing queries store rows in a bounded in-memory `ResultStore` keyed by result handle. The API fetches pages by job id and page index. Result data is not written to SQLite.

### Decision: Pane id is browser-provided but backend-authoritative per connection

The query API accepts a pane id and connection id. The backend uses those values to create or reuse a session record and driver connection for that pane/connection pair. Sessions are cleaned up on idle timeout or connection deletion in later slices; this slice provides explicit close/cancel-safe cleanup hooks where practical.

### Decision: REST polling before WebSockets

The first query implementation exposes submit, status, cancel, and page endpoints. WebSocket event publishing is deferred until workspace synchronization is implemented.

## Risks / Trade-offs

- Driver cancellation differs by dialect -> expose best-effort cancellation and structured status; tests use fakes for deterministic cancellation.
- In-memory results disappear on restart -> acceptable for v1 query execution because durable result data is explicitly a non-goal.
- Large results can exhaust memory -> enforce settings for default limit, max page size, and total stored cells/rows.
- Explicit transaction state is dialect-sensitive -> track obvious transaction commands and expose a conservative pane transaction state.

## Migration Plan

1. Add query domain, service, ports, adapters, result store, settings, routes, and tests.
2. Validate the OpenSpec change and run backend quality checks.
3. Rollback is code-only because this slice does not require a SQLite migration.

## Open Questions

- None for this slice.
