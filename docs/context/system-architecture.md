# System Architecture Context

## Runtime Topology

Production v1 is a single Docker container.

```text
Browser / Next.js static app
  | REST: commands and data fetches
  | WS: job status, pane state, workspace sync
FastAPI server
  |-- auth and vault unlock
  |-- application services
  |-- SQLite app database
  |-- query job manager
  |-- per-pane DB sessions
  |-- dialect adapters
  |-- temp result store
  |-- AI provider gateway
Postgres / MySQL / local AI endpoints
```

FastAPI is the only production runtime server. It serves built static Next.js assets and owns REST and WebSocket APIs.

## Trust Boundaries

- Browser is untrusted with respect to database credentials.
- Backend owns credentials, database sessions, query execution, generated SQL execution, result paging, and mutation safety.
- SQLite app storage is local to a mounted Docker volume.
- Saved database credentials are encrypted and locked until the admin passphrase unlocks the vault.
- AI providers receive schema metadata by default, not row/sample data.

## Network Exposure

The app binds to `127.0.0.1` by default. LAN or reverse-proxy exposure is opt-in and should be treated as a future hardening path, not the default v1 experience.

## State Authority

The backend is authoritative for:

- workspaces
- panes and query tabs
- database session lifecycle
- query jobs
- result-page handles
- audit/history metadata
- saved connection metadata

The frontend may cache data for responsiveness, but WebSocket invalidations and backend state remain authoritative.

## Primary Flow

1. User logs in with local admin passphrase.
2. Backend unlocks the vault for the server process lifetime/session policy.
3. User selects a saved connection or creates a new one.
4. A workspace pane establishes or reuses a backend database session.
5. Queries, edits, imports, and exports become backend jobs.
6. Job status is broadcast over WebSocket.
7. Result pages are fetched from backend temp storage.
8. Mutating actions are previewed and confirmed through normal review surfaces.
