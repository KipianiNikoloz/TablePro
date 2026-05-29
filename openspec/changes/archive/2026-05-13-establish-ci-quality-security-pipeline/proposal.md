## Why

TablePro now has a Python backend with migrations, security-sensitive vault behavior, saved connection credentials, and OpenSpec-backed intent. The repository needs automated quality and security gates before more database workflow code, frontend code, and packaging are added.

## What Changes

- Add GitHub Actions workflows for CI, scheduled security checks, CodeQL, dependency review, and a manual release scaffold.
- Add backend development dependencies for linting, formatting checks, dependency vulnerability scanning, and Python static security scanning.
- Validate OpenSpec changes in CI using the npm OpenSpec CLI.
- Keep Docker image publishing as a guarded scaffold until the packaging change adds a Dockerfile and release entrypoint.

## Capabilities

### New Capabilities

- `tablepro-ci-quality-security-pipeline`: Defines repository quality gates, security checks, and release scaffolding for TablePro.

### Modified Capabilities

- None.

## Impact

- Adds `.github/workflows/` CI/security/release workflow files.
- Updates backend dev dependencies and lockfile.
- Adds a new OpenSpec change for CI/CD quality and security behavior.
- Does not add Docker packaging, frontend checks, image scanning, SBOM generation, or production deployment.
