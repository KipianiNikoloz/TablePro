## Why

TablePro currently has only a deferred vault/auth boundary, but the next product workflows need a real server-side trust boundary before any database credentials can be saved or used. This change establishes the local setup, login/unlock, session, and encrypted secret-reference foundation without pulling in saved connections or query execution.

## What Changes

- Add one-time local admin setup for first run.
- Add passphrase login/unlock, lock, logout, and auth status APIs.
- Add HTTP-only cookie sessions with server-side session revocation and idle expiry.
- Add an encrypted vault for internal secret-reference create/read/update/delete/resolve behavior.
- Replace the deferred vault runtime state with real initialized/locked/unlocked status.
- Add SQLite persistence and migrations for vault state, auth sessions, and encrypted secret refs.
- Add safety tests proving raw passphrases, session tokens, derived keys, and decrypted secrets are not returned by APIs.

## Capabilities

### New Capabilities

- `tablepro-local-auth-vault`: Local admin setup, browser auth sessions, vault unlock state, and encrypted internal secret refs.

### Modified Capabilities

- None.

## Impact

- Backend API routes and schemas under `apps/backend/src/tablepro_backend/api`.
- Backend application services, vault port, and SQLite infrastructure adapters.
- Alembic migrations for app-local auth/vault tables.
- Backend dependencies for authenticated cookie signing and encryption.
- Runtime metadata response now reports real vault state instead of a deferred placeholder.
