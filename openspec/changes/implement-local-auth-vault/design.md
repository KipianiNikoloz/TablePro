## Context

The backend scaffold has a FastAPI runtime, SQLite app database migrations, status endpoints, and a placeholder `DeferredVaultService`. Product architecture requires local admin login, HTTP-only browser sessions, and server-side credential storage before connection workflows can safely persist database credentials.

This change is the first real trust-boundary slice. It must be useful for later connection APIs while avoiding a generic browser secret-manager feature or saved database connection model.

## Goals / Non-Goals

**Goals:**

- Support one-time local admin setup from an uninitialized app state.
- Unlock the vault from an admin passphrase and keep decrypted key material only in backend process memory.
- Issue revocable HTTP-only cookie sessions with idle expiry.
- Provide internal encrypted secret-reference CRUD for future connection credentials.
- Report initialized, authenticated, locked, and unlocked state without exposing secrets.

**Non-Goals:**

- Do not implement saved database connections, connection testing, query execution, or frontend UI.
- Do not expose generic secret CRUD over HTTP.
- Do not implement key rotation, multiple users, password reset, LAN/reverse-proxy hardening, or environment master keys.
- Do not persist raw passphrases, derived keys, session tokens, decrypted secrets, or database credentials.

## Decisions

### Decision: Use one-time setup API

Expose `POST /api/auth/setup` only when no vault state exists. This keeps local Docker first-run setup simple and testable without requiring env-seeded secrets.

Alternatives considered:

- Environment bootstrap: useful later for automation, but not the v1 default.
- Manual seed only: secure but unusable for the next browser login workflow.

### Decision: Use server-side sessions with HTTP-only cookies

Login sets an opaque session cookie. The backend stores only a hash of that token with created, last-seen, idle-expiry, and revoked timestamps. Logout revokes the current session; lock revokes active sessions and clears in-memory key material.

Alternatives considered:

- Bearer tokens returned to browser code: simpler for API clients, but weaker for browser credential handling.
- Unlock-only without browser session: insufficient for subsequent protected APIs.

### Decision: Use Fernet encryption with passphrase-derived key

Use `cryptography` Fernet for authenticated encryption of small secret values. Derive the Fernet key from the local admin passphrase using PBKDF2-HMAC-SHA256, a random per-install salt, and stored KDF metadata. Store an encrypted verifier so login can detect wrong passphrases before resolving secrets.

Alternatives considered:

- Hand-rolled encryption: rejected.
- Argon2id/Scrypt: viable, but PBKDF2-HMAC keeps dependencies and operational behavior simpler for this first local slice.

### Decision: Keep secret refs internal-only

Implement secret-reference CRUD as application/infrastructure behavior with tests, but do not add public `/api/secrets` endpoints. Future connection APIs will call this service when saving database credentials.

Alternatives considered:

- Protected generic HTTP CRUD: useful for manual testing, but exposes a broad product surface before the connection model exists.
- Unlock-only: would leave the next connection slice to invent storage under pressure.

## Risks / Trade-offs

- Weak local passphrases can weaken vault protection -> Require a minimum 12-character passphrase and keep the requirement explicit for v1.
- In-memory unlock state disappears on restart -> This matches the architecture requirement that the app locks after container restart.
- PBKDF2 is CPU-cost based rather than memory-hard -> Store KDF metadata so a future change can add rotation/migration.
- Cookie security depends on local deployment shape -> Use HTTP-only, SameSite=lax, and secure-cookie configuration that can be enabled for non-local deployments later.

## Migration Plan

1. Add an Alembic migration for vault state, auth sessions, and encrypted secret refs.
2. Add crypto/session settings with conservative local defaults.
3. Replace the deferred vault service with real vault, session, and internal secret-ref services.
4. Add auth routes and runtime state reporting.
5. Add unit, integration, API, and safety tests.

Rollback before release can drop the new migration and code. After users store secrets, rollback would require deleting local app state or adding a vault export/migration path in a later change.

## Open Questions

- None for this slice.
