## 1. OpenSpec Validation

- [x] 1.1 Validate `implement-query-execution` before implementation.

## 2. Domain, Ports, and Settings

- [x] 2.1 Add query domain models/errors, job/result-page types, and pane transaction state.
- [x] 2.2 Add query adapter and result-store port types.
- [x] 2.3 Add query execution settings for timeouts, page size, row limits, concurrency, and result-store bounds.

## 3. Service, Adapters, and API

- [x] 3.1 Implement the query service with job lifecycle, pane session reuse, cancellation, and result paging.
- [x] 3.2 Implement in-memory result storage.
- [x] 3.3 Implement Postgres/MySQL query adapters behind the query port.
- [x] 3.4 Add authenticated query request/response schemas and routes.
- [x] 3.5 Wire the query service into FastAPI app state and runtime metadata.
- [x] 3.6 Update backend README deferred-capabilities text.

## 4. Verification

- [x] 4.1 Add service tests for success, failure, paging, cancellation, locked vault, and pane isolation.
- [x] 4.2 Add API tests for auth, submit/status/cancel/page behavior, validation, and secret-safe responses.
- [x] 4.3 Run Ruff, pytest, and OpenSpec validation.
- [x] 4.4 Review git status for intended files only.
