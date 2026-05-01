# Security and Safety Context

## Authentication

V1 uses local admin login. Browser sessions use secure HTTP-only cookies with idle timeout. The app is locked after container restart until the admin passphrase unlocks the vault.

## Secret Vault

Database credentials are encrypted in the local SQLite app volume. The backend stores and resolves secret references; raw credentials must not be returned to browser code.

The vault key is derived from the admin passphrase for v1. Future automation may add an environment master key, but that is not v1 default.

## Exposure

Bind to `127.0.0.1` by default. Treat LAN or reverse-proxy deployment as opt-in and requiring extra security review.

## Production Safety

Connections have manual environment labels. Destructive or risky SQL on `prod` or production-like labels must require extra confirmation. Generated mutation SQL should always be previewable.

## Logging Privacy

Default logs should include event types, ids, durations, row counts, statuses, and structured error categories. They should avoid full SQL text, result data, credentials, and row values unless an explicit debug mode exists.

## Audit History

Audit/history records should store query and mutation metadata without storing result data by default. Mutating actions should record enough metadata to understand what happened: connection, timestamp, status, row count, and action type.

## AI Safety

AI-generated content is advisory until the user moves it through normal editor/review controls. The AI assistant must not have a direct execution path.
