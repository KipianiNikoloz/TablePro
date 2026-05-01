## Context

TablePro is being defined from a fresh repository that currently contains OpenSpec scaffolding and local Codex skill files. There is no application runtime code yet, so the first useful implementation is durable architecture context that later humans and agents can rely on.

The target product is a local-first, Docker-packaged browser database manager for solo developers. V1 will connect directly to Postgres and MySQL, run in a single container, serve a static Next.js app through FastAPI, keep database credentials server-side, and support querying, schema browsing, browser workspaces, inline row edits, CSV import/export, and an optional AI assistant.

## Goals / Non-Goals

**Goals:**

- Capture the TablePro v1 system architecture in OpenSpec.
- Add root `AGENTS.md` as the canonical agent entrypoint and context router.
- Add domain-sharded docs under `docs/context/` so agents can load focused context.
- Document pragmatic hexagonal backend architecture with stable ports at meaningful boundaries.
- Document the local-first trust model, vault behavior, query/session model, UI architecture, AI safety boundary, packaging, operations, and test strategy.
- Add a standard root `.gitignore` that excludes generated files, local data, secrets, and `.codex/`.

**Non-Goals:**

- Do not scaffold FastAPI, Next.js, Docker, database adapters, or runtime application code in this change.
- Do not implement OpenSpec archival in this change.
- Do not add team mode, SSH tunnels, cloud auth helpers, SSO, public plugin APIs, or external app database support.
- Do not version local `.codex/` skill scaffolding unless a future change explicitly decides to.

## Decisions

### Decision: Use one broad architecture capability

Create one OpenSpec capability, `tablepro-system-architecture`, for the initial architecture baseline.

Alternatives considered:

- Multiple narrow capabilities such as `database-workflows`, `ai-assistant`, and `operations`: more precise long term, but too heavy before runtime code exists.
- Docs-only capability: easier to implement, but weaker as durable product architecture.

Rationale: the first spec should be the backbone. Future changes can split or add narrower capabilities as implementation begins.

### Decision: Use root `AGENTS.md` as context orchestrator

`AGENTS.md` will be the first file agents read. It will route task domains to the minimum relevant docs shards and identify OpenSpec as the source of product/spec intent.

Alternatives considered:

- `docs/AGENTS.md`: keeps docs together but is less discoverable by common agent tooling.
- Duplicate root and docs agent files: useful later, but unnecessary duplication now.

Rationale: a root orchestrator gives agents a short, stable entrypoint without forcing them to load every architecture document.

### Decision: Store human/agent context in `docs/context/`

Domain docs will live under `docs/context/` and be split by architecture domain:

- product
- system architecture
- backend
- frontend
- database workflows
- security and safety
- AI assistant
- operations and packaging
- testing

Alternatives considered:

- `docs/architecture/`: good for humans, but less explicit as agent context.
- OpenSpec specs only: good for normative requirements, but too rigid for explanatory context.

Rationale: OpenSpec captures the durable contract; docs/context explains how to work with it.

### Decision: Document pragmatic hexagonal architecture

Backend context will describe inbound FastAPI adapters, application services, domain core, outbound ports, and infrastructure adapters. It will warn against excessive interface boilerplate inside simple flows.

Alternatives considered:

- Strict hexagonal architecture: stronger boundaries, but too much ceremony for an early solo-developer tool.
- Simple layered architecture: faster initially, but weaker for future database/AI/transport adapters.

Rationale: TablePro has important volatile boundaries: database drivers, app storage, secret vault, temp result storage, events, CSV handling, and AI providers.

### Decision: Ignore `.codex/` and standard generated files

The root `.gitignore` will ignore `.codex/`, local secrets, local app data, Python and Node caches, build outputs, logs, editor files, temp result files, and local SQLite volume files.

Alternatives considered:

- Minimal ignore file: likely creates noise as soon as implementation starts.
- No ignore file: leaves local agent files and generated output unguarded.

Rationale: the repository currently has untracked `.codex/` local skill files. These should stay local unless intentionally versioned later.

## Risks / Trade-offs

- Broad architecture spec may become large -> Keep requirements focused on enduring architectural behavior and put explanatory detail in docs/context.
- Docs can drift from OpenSpec -> `AGENTS.md` must instruct agents to update both when architecture decisions change.
- Ignoring `.codex/` may hide useful local skill edits -> Treat `.codex/` as local-only by default and create a future explicit change if the project wants to version agent skills.
- Pragmatic hexagonal architecture can become vague -> Name concrete ports and adapters in backend context and testing strategy.

## Migration Plan

1. Create the OpenSpec change artifacts.
2. Add `AGENTS.md`, `docs/context/` shards, and `.gitignore`.
3. Validate the OpenSpec change.
4. Leave archival for a later explicit action after review.

Rollback is simple because this change only adds docs/spec files and a `.gitignore`; remove the added files/directories if the architecture baseline is rejected.

## Open Questions

- None for this initial context package.
