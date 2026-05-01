## ADDED Requirements

### Requirement: Persistent system architecture context
The repository SHALL contain persistent TablePro system architecture context that is usable by both humans and coding agents before application runtime code exists.

#### Scenario: Architecture context exists
- **WHEN** a contributor inspects the repository
- **THEN** they can find a root agent entrypoint, domain-sharded context docs, and OpenSpec artifacts describing TablePro v1 architecture

#### Scenario: Context is implementation-ready
- **WHEN** an agent begins future implementation work
- **THEN** the context identifies the product goals, v1 scope, non-goals, architectural boundaries, and validation strategy without requiring prior chat history

### Requirement: Agent context orchestration
The repository SHALL include a root `AGENTS.md` file that acts as the canonical context orchestrator for coding agents.

#### Scenario: Agent routes by task domain
- **WHEN** an agent receives a task about a specific TablePro domain
- **THEN** `AGENTS.md` tells the agent which `docs/context/` shard or shards to read before acting

#### Scenario: Agent respects architectural intent
- **WHEN** an agent changes a system-level decision
- **THEN** `AGENTS.md` requires the agent to update the relevant OpenSpec and context docs rather than relying on chat-only decisions

### Requirement: Domain-sharded documentation
The repository SHALL contain domain-sharded context documentation under `docs/context/` for product, architecture, backend, frontend, database workflows, security and safety, AI, operations and packaging, and testing.

#### Scenario: Domain docs are discoverable
- **WHEN** a human or agent opens `docs/context/`
- **THEN** each major TablePro system domain has a named Markdown shard with focused context

#### Scenario: Domain docs avoid duplication
- **WHEN** a domain detail belongs to one shard
- **THEN** other shards reference the domain concept only as needed and do not duplicate full detail

### Requirement: Pragmatic hexagonal backend architecture
The backend architecture SHALL use pragmatic hexagonal architecture with explicit ports at meaningful system boundaries.

#### Scenario: Core logic avoids infrastructure coupling
- **WHEN** application/domain code defines workspaces, pane sessions, query jobs, edit batches, import plans, safety rules, audit events, or AI drafts
- **THEN** that code depends on ports rather than concrete database drivers, SQLite storage, filesystem temp storage, WebSocket publishing, or AI provider clients

#### Scenario: Infrastructure implements ports
- **WHEN** the system interacts with Postgres, MySQL, SQLite, encrypted secrets, result spill storage, WebSocket events, CSV files, or OpenAI-compatible AI providers
- **THEN** those integrations are implemented as infrastructure adapters behind outbound ports

### Requirement: Local-first single-container runtime
The TablePro v1 architecture SHALL define a local-first single-container runtime in which FastAPI serves the static Next.js app and owns backend APIs.

#### Scenario: Runtime topology is clear
- **WHEN** a contributor reads the architecture context
- **THEN** they understand that production v1 has one container, one FastAPI runtime server, static Next.js assets, typed REST APIs, and typed WebSocket events

#### Scenario: Localhost default is preserved
- **WHEN** the app is packaged for v1
- **THEN** it binds to `127.0.0.1` by default and treats LAN or reverse-proxy exposure as opt-in

### Requirement: Server-side trust boundary and vault
The TablePro v1 architecture SHALL keep database credentials and query execution server-side.

#### Scenario: Credentials are not exposed to browser code
- **WHEN** a browser client uses a saved database connection
- **THEN** raw database credentials remain in the backend vault and are not returned to the browser

#### Scenario: Vault requires unlock after restart
- **WHEN** the container restarts
- **THEN** encrypted saved credentials remain locked until the local admin passphrase unlocks the app

### Requirement: Database workflow architecture
The TablePro v1 architecture SHALL cover direct Postgres/MySQL connections, schema introspection, query execution, per-pane sessions, transactions, inline edits, and CSV import/export.

#### Scenario: Query jobs are modeled
- **WHEN** a user runs a query, import, export, or edit action
- **THEN** the backend represents it as a cancellable job with status, timing, row counts, errors, limits, and result-page access where applicable

#### Scenario: Safe row edits are modeled
- **WHEN** a user edits table rows inline
- **THEN** edits are previewed, require unique row identity, use optimistic concurrency checks, and apply transactionally

#### Scenario: CSV import is modeled
- **WHEN** a user imports CSV data into a new table
- **THEN** the workflow includes inferred schema, editable DDL preview, conflict handling, validation, and transactional execution

### Requirement: AI assistant execution boundary
The TablePro v1 architecture SHALL define the AI assistant as a draft-preparation feature that cannot directly execute database actions.

#### Scenario: AI drafts use normal review surfaces
- **WHEN** the AI assistant creates SQL, import, or edit suggestions
- **THEN** those suggestions are placed into the normal editor or review surfaces for explicit user execution

#### Scenario: AI context is private by default
- **WHEN** AI context is assembled
- **THEN** schema metadata is allowed by default and row/sample data requires explicit user inclusion

### Requirement: Operations and repository hygiene
The repository SHALL include baseline operational context and ignore rules for local development artifacts.

#### Scenario: Operational context is documented
- **WHEN** a contributor needs packaging, persistence, migration, backup, logging, or resource-limit guidance
- **THEN** the domain docs describe Docker packaging, SQLite volume behavior, migrations, backup/restore, redacted logging, and conservative resource defaults

#### Scenario: Generated and local files are ignored
- **WHEN** normal development creates caches, logs, local secrets, local app data, Node/Next outputs, Python outputs, editor files, or `.codex/`
- **THEN** the root `.gitignore` excludes those files from version control
