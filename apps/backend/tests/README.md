# Backend Test Layout

Tests are grouped by the kind of behavior they protect:

- `unit/`: fast tests for settings, pure application/domain behavior, and fake-port logic.
- `api/`: FastAPI route and response-contract tests.
- `integration/`: tests that touch real infrastructure adapters such as SQLite migrations.

Keep new tests in the narrowest category that proves the behavior. Broader end-to-end or browser tests should live outside this backend unit/API/integration suite when those surfaces exist.
