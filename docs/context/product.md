# Product Context

## Goal

TablePro is a browser-based database manager inspired by TablePlus, packaged as a Docker image for local use. It targets solo developers who want a fast database cockpit without installing a desktop app.

## V1 User

- Solo developer.
- Runs the app locally through Docker.
- Connects to development, staging, or production-like databases they can reach directly from the container.
- Wants a reliable query and browsing workflow with enough safety to avoid accidental destructive changes.

## V1 Scope

- Local password-protected browser app.
- Direct Postgres and MySQL connections.
- Server-side credential vault and query execution.
- Schema browser.
- SQL editor.
- Paged result grid.
- Query history and bookmarks.
- Browser workspaces with panes/tabs.
- Per-pane database sessions.
- Inline row edits with review before apply.
- CSV export and CSV import into new tables.
- Optional AI side panel that drafts SQL/import/edit actions.

## Non-Goals

- Team accounts, sharing, RBAC, invites, or SSO.
- SSH tunnels or cloud-provider connection helpers.
- Public plugin API.
- External app database.
- Durable caching of query result data.
- Schema designer or full database administration suite.
- AI direct execution of database actions.

## Product Bias

Prefer a focused database workstation over a generic admin portal. V1 should feel dense, quiet, fast, and reliable. Avoid landing-page thinking inside the app: the first screen should help the user connect, browse, query, and act.

Frontend visual implementation borrows its visual rulebook from `static/helixdb_design_deck.pdf`, but product naming remains TablePro unless a future OpenSpec change explicitly approves a rename.
