## ADDED Requirements

### Requirement: Pull request quality gates
The repository SHALL run automated quality gates for backend code on pull requests and default-branch pushes.

#### Scenario: Backend quality checks pass
- **WHEN** a pull request changes backend or workflow files
- **THEN** CI installs the backend from the lockfile and runs lint, formatting, tests, and OpenSpec validation

#### Scenario: Lockfile drift is detected
- **WHEN** backend dependency declarations and the lockfile are out of sync
- **THEN** CI fails before tests rely on an unreproducible dependency set

### Requirement: Security scanning gates
The repository SHALL run automated security checks for dependency, code, and secret risks.

#### Scenario: Dependency vulnerability found
- **WHEN** a runtime dependency has a known blocking vulnerability
- **THEN** the security workflow reports the vulnerability and fails the check

#### Scenario: Secret material is committed
- **WHEN** tracked repository files contain detected secret material
- **THEN** the security workflow fails without requiring application runtime startup

#### Scenario: Static security issue found
- **WHEN** backend source contains a Bandit-detected security issue
- **THEN** the security workflow reports the finding and fails the check

### Requirement: Release scaffold
The repository SHALL document the future release automation shape without publishing artifacts before Docker packaging exists.

#### Scenario: Manual release dry run
- **WHEN** the release workflow is manually run before Docker packaging exists
- **THEN** it runs validation checks and reports that Docker publishing is intentionally disabled

#### Scenario: Docker publish remains disabled
- **WHEN** the release workflow runs before a Dockerfile and packaging change exist
- **THEN** it does not publish an image
