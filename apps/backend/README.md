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

This first spine does not implement login, credential encryption, saved database connections, query execution, WebSockets, or Docker packaging.
