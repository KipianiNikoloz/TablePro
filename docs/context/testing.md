# Testing Context

## Test Pyramid

Use fast unit tests for domain/application logic, contract tests for ports, integration tests for real database adapters, and browser tests for core workflows.

## Unit Tests

Unit-test with fake ports:

- query job lifecycle
- pane-session state
- transaction state modeling
- edit planning
- optimistic concurrency decisions
- import planning
- safety rules for risky labels
- AI draft boundaries
- audit event creation

## Contract Tests

Contract-test outbound ports:

- `DialectAdapter`
- `AppStateRepository`
- `SecretVault`
- `ResultStore`
- `AuditLog`
- `EventBus`
- `AIProvider`

Contracts should document expected errors, cancellation behavior, type mapping, and capability declarations.

## Integration Tests

Use real Postgres and MySQL test containers for:

- connection tests
- schema introspection
- cached refresh
- SELECT queries
- write queries
- cancellation
- pagination
- explicit transactions
- inline edits
- CSV import/export
- structured error mapping

## Frontend and End-to-End Tests

Browser tests should cover:

- login/unlock
- connection creation
- workspace/pane creation
- SQL editor run/cancel
- result pagination
- inline edit review/apply
- CSV import wizard
- AI draft-to-editor flow
- multi-window synchronization

## Safety Tests

Include explicit tests for:

- browser never receives raw DB credentials
- prod-label destructive-query confirmation
- missing primary key disables editing
- failed edit rolls back
- AI cannot directly execute
- logs redact credentials/result data by default

## Resource Tests

Exercise limits for long queries, wide result sets, abandoned browser windows, large exports, large imports, and full temp result stores.
