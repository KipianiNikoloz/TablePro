## 1. OpenSpec Architecture Baseline

- [x] 1.1 Create `tablepro-system-architecture` spec requirements for persistent architecture context.
- [x] 1.2 Create the design document describing the docs architecture, pragmatic hexagonal backend style, and repository hygiene choices.

## 2. Agent Context Orchestration

- [x] 2.1 Add root `AGENTS.md` as the canonical agent entrypoint.
- [x] 2.2 Include a task-domain routing table from `AGENTS.md` to the relevant `docs/context/` shards.
- [x] 2.3 Instruct agents to treat OpenSpec as source intent and update docs/specs when architecture decisions change.

## 3. Domain Context Shards

- [x] 3.1 Add `docs/context/product.md` for goals, scope, non-goals, and user model.
- [x] 3.2 Add `docs/context/system-architecture.md` for runtime topology, trust boundaries, and data flow.
- [x] 3.3 Add `docs/context/backend.md` for FastAPI, pragmatic hexagonal architecture, ports, adapters, jobs, and sessions.
- [x] 3.4 Add `docs/context/frontend.md` for the static Next.js app shell, workspaces, sync, editor, and grid expectations.
- [x] 3.5 Add `docs/context/database-workflows.md` for connections, schema cache, querying, transactions, edits, and CSV import/export.
- [x] 3.6 Add `docs/context/security-and-safety.md` for auth, vault, localhost default, prod labels, destructive-query friction, and logging privacy.
- [x] 3.7 Add `docs/context/ai-assistant.md` for AI context, providers, draft boundaries, and safety rules.
- [x] 3.8 Add `docs/context/operations-and-packaging.md` for Docker packaging, SQLite volume, migrations, backup/restore, and resource limits.
- [x] 3.9 Add `docs/context/testing.md` for unit, contract, integration, UI, safety, and resource-limit testing.

## 4. Repository Hygiene

- [x] 4.1 Add root `.gitignore` for `.codex/`, secrets, Python/Node/Next generated files, logs, temp files, local SQLite data, and editor files.
- [x] 4.2 Verify `.gitignore` does not exclude OpenSpec files, docs, or future source directories.

## 5. Validation

- [x] 5.1 Run OpenSpec validation for `establish-system-design-context`.
- [x] 5.2 Review git status to confirm only intended docs/spec/context files are added.
