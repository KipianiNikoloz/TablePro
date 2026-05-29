## ADDED Requirements

### Requirement: Saved direct database connections
The backend SHALL persist saved direct Postgres and MySQL connection metadata in the local app database.

#### Scenario: Create saved connection
- **WHEN** an authenticated browser submits valid direct connection metadata and a password while the vault is unlocked
- **THEN** the backend saves the metadata, stores the password through the vault, and returns a connection response without secret material

#### Scenario: List saved connections
- **WHEN** an authenticated browser lists saved connections
- **THEN** the backend returns saved connection metadata without passwords, encrypted blobs, decrypted secrets, or internal secret refs

#### Scenario: Update saved connection
- **WHEN** an authenticated browser updates saved connection metadata or replaces its password while the vault is unlocked
- **THEN** the backend updates the record and keeps password storage behind the vault boundary

#### Scenario: Delete saved connection
- **WHEN** an authenticated browser deletes a saved connection while the vault is unlocked
- **THEN** the backend removes the connection from normal listings and deletes the associated password secret ref

### Requirement: Credential-safe connection APIs
The backend SHALL protect connection management APIs with local admin authentication and avoid exposing raw credential material.

#### Scenario: Unauthenticated request rejected
- **WHEN** a browser without a valid local admin session calls a connection API
- **THEN** the backend rejects the request without performing the operation

#### Scenario: Locked vault rejects credential operations
- **WHEN** a saved connection operation needs to store or resolve a password while the vault is locked
- **THEN** the backend rejects the operation without returning decrypted secret material

#### Scenario: Response redaction
- **WHEN** a connection API returns a success or failure response
- **THEN** the response omits raw passwords, decrypted secrets, encrypted blobs, and internal secret-reference identifiers

### Requirement: Direct connection testing
The backend SHALL test direct Postgres and MySQL connectivity without adding general query execution behavior.

#### Scenario: Test provided connection details
- **WHEN** an authenticated browser submits direct connection details and a password while the vault is unlocked
- **THEN** the backend attempts a connectivity check and returns structured success or failure metadata without persisting the connection

#### Scenario: Test saved connection
- **WHEN** an authenticated browser asks to test a saved connection while the vault is unlocked
- **THEN** the backend resolves the saved password server-side, attempts a connectivity check, and returns structured success or failure metadata without exposing credentials

#### Scenario: Unsupported dialect rejected
- **WHEN** a browser submits a dialect outside the supported Postgres/MySQL set
- **THEN** the backend rejects the request before attempting a driver connection
