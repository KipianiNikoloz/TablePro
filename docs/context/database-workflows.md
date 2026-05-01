# Database Workflows Context

## Connections

V1 supports direct Postgres and MySQL connections by host, port, database, username, and credential reference. Direct transport is the only implemented transport, but model connection transport separately enough that SSH/cloud transport can be added later.

Connections have manual environment labels such as `local`, `staging`, and `prod`.

## Schema Introspection

Schema metadata is cached per connection. The cache is refreshed manually and invalidated after known DDL/import actions. Schema snapshots should include tables, columns, primary keys, unique identities, indexes, and relationships where the dialect adapter can provide them.

## Querying

User-submitted SQL runs through the backend query job manager. Defaults should include row limits, timeouts, and cancellation support. Result data is served from temporary backend result storage in pages.

## Transactions

Explicit `BEGIN`, `COMMIT`, and `ROLLBACK` affect only the current pane session. The UI must visibly show pane transaction state so users know when a session is inside an open transaction.

## Inline Row Edits

Inline edits are allowed only when the result set or table row can be uniquely identified by primary key or unique identity.

Edit behavior:

- accumulate changes as a visible diff
- always preview generated SQL
- apply changes in a transaction
- use optimistic concurrency checks
- require affected rows to match expectations
- rollback and show structured errors on failure

## CSV Export

CSV export is available for query results and table data. Exports run as backend jobs and must respect resource limits.

## CSV Import

CSV import supports creating new tables in v1.

Import flow:

1. Upload/select CSV through the browser.
2. Backend parses a sample and infers schema.
3. UI presents editable table name, column names, column types, nullability, and primary key choice.
4. Backend generates dialect-specific DDL and import SQL.
5. User previews SQL.
6. Backend executes transactionally.
7. Schema cache invalidates after success.
