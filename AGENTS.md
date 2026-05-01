# TablePro Agent Context

TablePro is a local-first, Docker-packaged browser database manager for solo developers. The product target is a browser UI with a server-side backend that owns database credentials, query execution, database sessions, result paging, inline edits, CSV import/export, and optional AI-assisted drafting.

OpenSpec is the source of product and architecture intent. Start with `openspec/changes/establish-system-design-context/` while this change is active. After archival, use the corresponding files under `openspec/specs/`.

## Architecture Rules

- Use pragmatic hexagonal architecture for the backend.
- Keep application/domain behavior independent from concrete database drivers, SQLite storage, filesystem temp storage, WebSocket publishing, CSV libraries, and AI provider clients.
- Put volatile integrations behind explicit ports only where the boundary matters.
- Do not add interface boilerplate inside simple application flows unless it protects a real boundary.
- Browser code must never receive raw database credentials.
- AI can draft actions only; normal editor/review surfaces remain the execution boundary.

## Context Routing

Load the smallest useful set of shards before working:

| Task domain | Read first |
| --- | --- |
| Product scope, v1 goals, non-goals | `docs/context/product.md` |
| Runtime topology, trust boundaries, system flow | `docs/context/system-architecture.md` |
| FastAPI backend, hexagonal ports/adapters, jobs, sessions | `docs/context/backend.md` |
| UI/design system, visual identity, layout density, shadcn composition | `docs/context/ui-design-system.md` |
| Next.js frontend, workspaces, grids, state sync | `docs/context/ui-design-system.md` then `docs/context/frontend.md` |
| Connections, schema, queries, edits, imports, exports | `docs/context/database-workflows.md` |
| Auth, vault, prod safety, logging privacy | `docs/context/security-and-safety.md` |
| AI assistant, provider config, prompt/context boundaries | `docs/context/ai-assistant.md` |
| Docker packaging, SQLite volume, migrations, backup, limits | `docs/context/operations-and-packaging.md` |
| Test strategy and acceptance coverage | `docs/context/testing.md` |

For any frontend or UI implementation work, read `docs/context/ui-design-system.md` before editing components, styles, layout, screenshots, or frontend tests.

## Change Discipline

- If you change architecture intent, update OpenSpec and the relevant `docs/context/` shard in the same change.
- If a decision is only local implementation detail, keep it near the implementation instead of inflating global context.
- Do not treat chat history as persistent project memory; capture durable decisions in docs/specs.
- Keep generated files, local secrets, app volumes, and local agent scaffolding out of version control according to `.gitignore`.
