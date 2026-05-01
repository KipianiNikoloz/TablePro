# Backend Context

## Stack

- FastAPI async backend.
- Python application services.
- Native database drivers behind dialect adapters.
- SQLite app database for local persistent state.
- WebSocket channel for live updates.
- In-process jobs with bounded pools where drivers require blocking work.

## Pragmatic Hexagonal Architecture

Use hexagonal architecture at meaningful boundaries:

```text
FastAPI inbound adapters
  -> application services
  -> domain core
  -> outbound ports
  -> infrastructure adapters
```

Do not create interfaces for every helper. Use ports where implementation volatility matters.

## Application Services

Expected service boundaries:

- `WorkspaceService`: workspaces, panes, tabs, layout state, presence.
- `ConnectionService`: connection metadata, testing, labels, vault refs.
- `QueryService`: query submission, job lifecycle, cancellation, paging.
- `EditService`: edit batch planning, SQL preview, transactional apply.
- `ImportExportService`: CSV parsing, export jobs, import plans, DDL preview.
- `AIService`: context assembly and draft action generation.
- `VaultService`: unlock state and secret reference resolution.

## Domain Concepts

- `Connection`
- `Workspace`
- `Pane`
- `PaneSession`
- `QueryJob`
- `ResultPage`
- `SchemaSnapshot`
- `EditBatch`
- `ImportPlan`
- `AuditEvent`
- `AIDraftAction`

## Outbound Ports

- `DialectAdapter`: connect, introspect, run, cancel, quote, map types, generate edit SQL, generate import DDL.
- `AppStateRepository`: saved metadata, workspaces, history, bookmarks, schema cache, migrations.
- `SecretVault`: encrypt, decrypt, unlock, rotate, return secret refs.
- `ResultStore`: bounded temporary storage for result pages and export handles.
- `AuditLog`: mutation/query metadata without storing result data.
- `EventBus`: publish typed workspace/job/session events.
- `AIProvider`: call OpenAI-compatible or future model providers.

## Query Jobs

Every query, edit apply, import, and export is a job with:

- id
- connection id
- pane/session id
- status
- timestamps and duration
- cancellation handle
- row counts where available
- structured error
- resource-limit metadata
- result handle where applicable

## Sessions

Use per-pane database sessions. Pane-scoped sessions make temp tables, explicit transactions, and cancellation understandable. Clean up sessions on idle timeout, workspace close, browser disconnect grace expiry, or connection deletion.
