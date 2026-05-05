## ADDED Requirements

### Requirement: Runnable FastAPI backend spine
The repository SHALL contain a backend service under `apps/backend` that can be installed, tested, and run locally with documented `uv` commands.

#### Scenario: Developer starts backend locally
- **WHEN** a developer installs backend dependencies and runs the local development command
- **THEN** a FastAPI application starts and exposes the backend status endpoints

#### Scenario: Backend has implementation-ready boundaries
- **WHEN** a contributor inspects the backend package
- **THEN** the package layout separates inbound API adapters, application services, domain concepts, outbound ports, infrastructure adapters, configuration, and tests

### Requirement: App database migration baseline
The backend SHALL include an explicit SQLite app database migration baseline for local persistent state.

#### Scenario: App database initializes
- **WHEN** the backend starts with an empty configured data directory
- **THEN** it creates or opens the SQLite app database and applies the initial migration

#### Scenario: Migration readiness is visible
- **WHEN** readiness is checked
- **THEN** the backend reports whether the app database is reachable and at the expected migration state

### Requirement: Operational status APIs
The backend SHALL expose narrow operational status APIs for liveness, readiness, and runtime metadata.

#### Scenario: Liveness check responds
- **WHEN** `GET /healthz` is requested
- **THEN** the backend returns process liveness without depending on database readiness

#### Scenario: Readiness check reports dependencies
- **WHEN** `GET /readyz` is requested
- **THEN** the backend returns readiness based on app database and migration checks

#### Scenario: Runtime metadata is redacted
- **WHEN** `GET /api/runtime` is requested
- **THEN** the response includes useful local runtime metadata but does not expose secrets, credentials, connection strings, or raw vault material

### Requirement: Vault boundary placeholder
The backend SHALL prepare a vault/auth boundary without implementing real login or credential encryption in this change.

#### Scenario: Vault behavior is explicitly deferred
- **WHEN** a contributor inspects the backend services and tests
- **THEN** the code makes clear that passphrase login, encryption, saved database credentials, and vault unlock flows are deferred to a future focused change
