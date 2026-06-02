## ADDED Requirements

### Requirement: Authenticated query submission
The backend SHALL allow authenticated browser sessions to submit SQL jobs for saved database connections without exposing raw database credentials.

#### Scenario: Submit query for saved connection
- **WHEN** an authenticated browser submits SQL with a saved connection id and pane id while the vault is unlocked
- **THEN** the backend resolves credentials server-side, creates a query job, and returns job metadata without passwords, encrypted blobs, connection strings, or secret-reference identifiers

#### Scenario: Unauthenticated query rejected
- **WHEN** a browser without a valid local admin session submits a query
- **THEN** the backend rejects the request without resolving credentials or contacting the target database

#### Scenario: Locked vault query rejected
- **WHEN** an authenticated browser submits a query while the vault is locked
- **THEN** the backend rejects the request without returning decrypted secret material

### Requirement: Pane-scoped database sessions
The backend SHALL associate query execution with pane-scoped database sessions for each saved connection.

#### Scenario: Reuse pane session
- **WHEN** multiple queries are submitted for the same saved connection and pane id
- **THEN** the backend reuses the pane session where practical so explicit transaction state remains pane-scoped

#### Scenario: Isolate different panes
- **WHEN** queries are submitted for different pane ids
- **THEN** the backend keeps their database sessions and transaction state separate

### Requirement: Query job lifecycle
The backend SHALL model each submitted query as a job with status, timing, row counts, structured error metadata, cancellation state, and resource-limit metadata.

#### Scenario: Successful query job
- **WHEN** a submitted query completes successfully
- **THEN** the backend marks the job succeeded and reports timing, row count, and result metadata where applicable

#### Scenario: Failed query job
- **WHEN** a submitted query fails
- **THEN** the backend marks the job failed and returns a structured error without exposing credentials or row data beyond the error metadata

#### Scenario: Cancel query job
- **WHEN** an authenticated browser requests cancellation for a running query job
- **THEN** the backend requests driver cancellation and marks the job cancelled or failed with structured metadata

### Requirement: Paged result access
The backend SHALL return result rows through temporary paged result access instead of requiring the browser to hold all rows at once.

#### Scenario: Fetch result page
- **WHEN** an authenticated browser requests a valid page for a succeeded result-producing query job
- **THEN** the backend returns the requested columns, rows, page index, page size, total row count where known, and limit metadata

#### Scenario: Missing result page rejected
- **WHEN** a browser requests result data for a job without a result handle or an out-of-range page
- **THEN** the backend returns a structured failure without exposing unrelated job or credential data

#### Scenario: Result storage is temporary
- **WHEN** the backend stores query results for page access
- **THEN** result rows remain in bounded temporary backend storage and are not persisted to the app SQLite database
