## Why

TablePro needs a durable system-design baseline before application code exists, so future humans and agents can build from the same architectural intent instead of rediscovering product boundaries each turn.

This change captures the full v1 architecture as OpenSpec-backed context and adds agent-readable documentation that routes work by domain.

## What Changes

- Establish the TablePro v1 system architecture as persistent OpenSpec context.
- Add a root `AGENTS.md` context orchestrator for coding agents.
- Add domain-sharded human/agent docs under `docs/context/`.
- Document the pragmatic hexagonal backend architecture, trust boundaries, runtime topology, database workflows, AI boundaries, operations, and testing strategy.
- Add a root `.gitignore` for standard generated files, local secrets, local app data, and `.codex/`.

## Capabilities

### New Capabilities

- `tablepro-system-architecture`: Defines the persistent architecture, documentation, agent-context routing, and repository hygiene baseline for TablePro v1.

### Modified Capabilities

- None.

## Impact

- Adds OpenSpec artifacts for the first architectural capability.
- Adds root agent instructions and domain context docs.
- Adds a baseline `.gitignore`.
- Does not scaffold application runtime code.
