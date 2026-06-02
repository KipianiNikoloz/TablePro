# TablePro Backend

FastAPI backend spine for TablePro.

## Local Development

```powershell
uv sync
uv run pytest
uv run uvicorn tablepro_backend.main:app --reload
```

If `uv` is not installed locally, install it before using these commands. The backend reads settings from environment variables prefixed with `TABLEPRO_`.

Useful settings:

- `TABLEPRO_DATA_DIR`: local app data directory. Defaults to `data`.
- `TABLEPRO_SQLITE_PATH`: SQLite app database path. Defaults to `<TABLEPRO_DATA_DIR>/tablepro.sqlite3`.
- `TABLEPRO_LOG_LEVEL`: logging level. Defaults to `INFO`.
- `TABLEPRO_AUTH_SESSION_IDLE_TIMEOUT_SECONDS`: local browser session idle timeout. Defaults to `1800`.
- `TABLEPRO_AUTH_SESSION_COOKIE_SECURE`: set to `true` for HTTPS deployments. Defaults to `false` for localhost development.

The backend supports one-time local setup, passphrase login/unlock, HTTP-only cookie sessions, encrypted internal secret references, saved database connections, schema introspection, and backend-owned query execution. It does not yet implement WebSockets, frontend serving, query history/bookmarks, inline edits, CSV import/export, AI drafting, or Docker packaging.
