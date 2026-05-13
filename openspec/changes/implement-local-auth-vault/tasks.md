## 1. OpenSpec Validation

- [x] 1.1 Validate `implement-local-auth-vault` before implementation.

## 2. Persistence and Configuration

- [x] 2.1 Add backend dependencies and settings for vault KDF, session cookie, idle timeout, and local cookie security.
- [x] 2.2 Add an Alembic migration for vault state, auth sessions, and encrypted secret refs.

## 3. Vault and Session Services

- [x] 3.1 Implement crypto helpers for passphrase-derived Fernet keys, encrypted verifier values, and secret encryption/decryption.
- [x] 3.2 Implement SQLite-backed vault state and encrypted secret-ref repository behavior.
- [x] 3.3 Implement session creation, validation, idle expiry refresh, revocation, and lock behavior.

## 4. Auth API and Runtime State

- [x] 4.1 Add auth request/response schemas and routes for status, setup, login, logout, and lock.
- [x] 4.2 Wire services into FastAPI app state and update runtime metadata to report real vault state.
- [x] 4.3 Ensure APIs never return raw passphrases, derived keys, salts, session tokens, encrypted blobs, or decrypted secrets.

## 5. Verification

- [x] 5.1 Add unit tests for KDF/verifier behavior, secret encryption/decryption, locked-state errors, and passphrase validation.
- [x] 5.2 Add API tests for setup, duplicate setup, login failure/success, status, logout, lock, and cookie behavior.
- [x] 5.3 Add integration tests proving migrations create vault tables and secret refs persist encrypted data only.
- [x] 5.4 Run backend tests and OpenSpec validation.
- [x] 5.5 Review git status for intended files only.
