## Context

The current repo is backend-only Python under `apps/backend`, uses `uv`, pytest, Alembic, Ruff configuration, and OpenSpec. There is no Dockerfile, frontend app, or existing GitHub workflow. The first pipeline should make the existing backend safer without inventing release behavior for artifacts that do not exist yet.

## Goals / Non-Goals

**Goals:**

- Gate pull requests and default-branch pushes on backend lint, formatting, tests, lockfile consistency, and OpenSpec validation.
- Run dependency vulnerability, Python static security, dependency review, CodeQL, and secret-scanning checks.
- Add a manual release workflow that records the intended Docker publishing shape but cannot publish until packaging exists.

**Non-Goals:**

- Do not build or publish Docker images before a packaging change adds a Dockerfile.
- Do not add frontend, browser, container, SBOM, or signing checks before those artifacts exist.
- Do not require live Postgres/MySQL services for the current unit/API test suite.

## Decisions

### Decision: Use GitHub Actions

GitHub Actions is the target CI/CD platform. Workflows use official actions where possible and plain package-manager commands for project tools.

### Decision: Split CI and security workflows

`ci.yml` runs fast quality gates on PRs and pushes. `security.yml` runs PR security checks and scheduled security scans. This keeps normal feedback quick while still making security checks visible and independently schedulable.

### Decision: Keep release as manual scaffold

`release.yml` is `workflow_dispatch` only and fails only if the current quality gates fail. Docker publish behavior is represented as a guarded placeholder until packaging exists.

## Risks / Trade-offs

- OpenSpec is installed from npm in CI, so npm registry availability affects validation.
- `pip-audit` can introduce newly failing builds when upstream advisories are published. This is intentional for runtime dependency risk.
- `bandit` can have false positives as backend code grows. Keep tests excluded and tune only with explicit comments/configuration when needed.

## Migration Plan

1. Add OpenSpec artifacts and validate the change.
2. Add backend dev dependencies and lockfile updates.
3. Add GitHub Actions workflows.
4. Run local backend quality, tests, security checks, and OpenSpec validation.

## Open Questions

- None for this slice.
