## Context

Saved connections contain the metadata and vault-backed credentials needed to reach Postgres/MySQL databases. Schema introspection should consume that boundary without introducing arbitrary query execution. The output is durable app metadata that supports browsing and later editing/query planning.

## Goals / Non-Goals

**Goals:**

- Persist the latest schema snapshot per saved connection.
- Refresh schema snapshots manually through an authenticated API.
- Include tables, columns, primary keys, unique identities, indexes, and relationships where available.
- Preserve the previous successful snapshot if a refresh fails.
- Keep API responses secret-safe.

**Non-Goals:**

- Do not execute user SQL or return table row data.
- Do not add pane sessions, result paging, CSV import/export, or frontend UI.
- Do not add automatic refresh/invalidation beyond storing manual refresh results.
- Do not require live database services in the default unit/API test suite.

## Decisions

### Decision: Store snapshot JSON in SQLite

The app database stores the latest schema snapshot as JSON text keyed by connection id. This avoids premature relational modeling of dialect metadata while keeping the snapshot durable and easy to replace atomically.

### Decision: GET is cache-only

`GET /api/connections/{connection_id}/schema` returns the latest cached snapshot or a clear cache-miss response. It does not implicitly unlock the vault or reach the target database.

### Decision: Refresh requires unlocked vault

`POST /api/connections/{connection_id}/schema/refresh` resolves the saved password server-side, runs dialect introspection, stores the new snapshot, and returns it. If introspection fails, the previous snapshot remains intact.

## Risks / Trade-offs

- Dialect metadata can vary by permissions and database version. Adapters should return best-effort supported fields and structured errors.
- JSON storage is less queryable than normalized tables, but it is the right shape for a v1 cache where snapshots are fetched by connection.
- Live database integration tests are valuable but should be separate from the default suite until CI has database services.

## Migration Plan

1. Add a `schema_snapshots` migration.
2. Add domain models and repository serialization.
3. Add dialect introspection port and Postgres/MySQL implementations.
4. Add service and API endpoints.
5. Add fake-adapter service/API tests and lightweight adapter query-shape tests.

## Open Questions

- None for this slice.
