## 1. OpenSpec Validation

- [x] 1.1 Create and validate `establish-ci-quality-security-pipeline`.

## 2. Backend Tooling

- [x] 2.1 Add backend dev dependencies for Ruff, pip-audit, and Bandit.
- [x] 2.2 Update the backend lockfile.

## 3. GitHub Actions

- [x] 3.1 Add CI workflow for backend install, lockfile check, Ruff check, Ruff format check, pytest, and OpenSpec validation.
- [x] 3.2 Add security workflow for dependency review, pip-audit, Bandit, CodeQL, and Gitleaks.
- [x] 3.3 Add manual release scaffold with guarded Docker publishing placeholder.

## 4. Verification

- [x] 4.1 Run backend lint, format check, tests, pip-audit, and Bandit locally.
- [x] 4.2 Run OpenSpec validation.
- [x] 4.3 Review git status for intended files only.
