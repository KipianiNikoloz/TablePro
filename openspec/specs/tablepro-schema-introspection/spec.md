## ADDED Requirements

### Requirement: Cached schema snapshots
The backend SHALL persist the latest schema snapshot for each saved database connection.

#### Scenario: Schema cache miss
- **WHEN** an authenticated browser requests schema for a saved connection with no refreshed snapshot
- **THEN** the backend returns a clear cache-miss response without contacting the target database

#### Scenario: Schema cache hit
- **WHEN** an authenticated browser requests schema for a saved connection with a refreshed snapshot
- **THEN** the backend returns the cached schema metadata without credentials or row data

### Requirement: Manual schema refresh
The backend SHALL manually refresh schema snapshots for saved direct Postgres/MySQL connections.

#### Scenario: Successful refresh
- **WHEN** an authenticated browser requests schema refresh while the vault is unlocked
- **THEN** the backend resolves the saved credential server-side, introspects the target database, stores the latest snapshot, and returns it

#### Scenario: Failed refresh preserves previous snapshot
- **WHEN** a refresh fails after a previous successful snapshot exists
- **THEN** the backend returns a structured failure and does not overwrite the previous snapshot

#### Scenario: Locked vault rejects refresh
- **WHEN** a browser requests schema refresh while the vault is locked
- **THEN** the backend rejects the operation without returning decrypted secret material

### Requirement: Schema metadata coverage
The backend SHALL include table, column, key, index, and relationship metadata where the dialect adapter can provide it.

#### Scenario: Snapshot metadata shape
- **WHEN** a schema snapshot is returned
- **THEN** it includes tables, columns, primary keys, unique identities, indexes, relationships, dialect, connection id, and refresh timestamp

#### Scenario: Secret-safe responses
- **WHEN** schema APIs return success or failure responses
- **THEN** responses omit raw passwords, encrypted blobs, connection strings, and internal secret-reference identifiers
