## ADDED Requirements

### Requirement: Local admin setup
The backend SHALL support one-time local admin setup before the vault has been initialized.

#### Scenario: Auth status before setup
- **WHEN** a browser requests auth status before vault initialization
- **THEN** the backend reports that setup is required, the browser is unauthenticated, and the vault is locked

#### Scenario: Successful first setup
- **WHEN** a valid passphrase is submitted before vault initialization
- **THEN** the backend initializes vault state, creates an authenticated browser session, and unlocks the vault in process memory

#### Scenario: Duplicate setup is rejected
- **WHEN** setup is submitted after vault initialization
- **THEN** the backend rejects the request without changing the existing vault state

### Requirement: Local login and session lifecycle
The backend SHALL authenticate the local admin passphrase and manage revocable HTTP-only browser sessions.

#### Scenario: Successful login
- **WHEN** the initialized app receives the correct admin passphrase
- **THEN** the backend unlocks the vault in process memory and returns an HTTP-only cookie session

#### Scenario: Failed login
- **WHEN** the initialized app receives an incorrect admin passphrase
- **THEN** the backend rejects login and does not create a browser session

#### Scenario: Session-authenticated status
- **WHEN** a browser requests auth status with a valid unexpired session
- **THEN** the backend reports the browser as authenticated and reports whether the vault is unlocked

#### Scenario: Logout revokes current session
- **WHEN** an authenticated browser logs out
- **THEN** the backend revokes the current session and clears the browser session cookie

#### Scenario: Lock revokes sessions
- **WHEN** an authenticated browser locks the app
- **THEN** the backend clears in-process vault key material and revokes active browser sessions

### Requirement: Encrypted internal secret refs
The backend SHALL provide internal encrypted secret-reference storage for future database credential workflows.

#### Scenario: Secret ref stores encrypted data
- **WHEN** application code stores a secret value while the vault is unlocked
- **THEN** the backend persists only encrypted secret data and returns an opaque secret reference

#### Scenario: Secret ref resolves while unlocked
- **WHEN** application code resolves an existing secret reference while the vault is unlocked
- **THEN** the backend returns the decrypted secret value to backend code only

#### Scenario: Secret ref resolution requires unlock
- **WHEN** application code resolves a secret reference while the vault is locked
- **THEN** the backend rejects the operation without returning decrypted secret material

### Requirement: Secret-safe API responses
The backend SHALL avoid returning raw vault material, passphrases, session tokens, or decrypted secrets to browser code.

#### Scenario: Runtime metadata is secret-safe
- **WHEN** runtime or auth status APIs are requested
- **THEN** responses do not include raw passphrases, derived keys, salts, encrypted blobs, decrypted secrets, or session tokens

#### Scenario: Browser has no generic secret API
- **WHEN** the local auth vault slice is complete
- **THEN** the backend exposes no generic browser-facing secret-reference CRUD API
