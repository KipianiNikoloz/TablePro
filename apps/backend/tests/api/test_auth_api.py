from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from tablepro_backend.core.config import Settings
from tablepro_backend.main import create_app

PASSPHRASE = "correct horse battery staple"


def _client(local_tmp_path: Path) -> TestClient:
    settings = Settings(
        data_dir=local_tmp_path,
        sqlite_path=local_tmp_path / "tablepro.sqlite3",
        vault_kdf_iterations=1000,
    )
    return TestClient(create_app(settings))


def test_auth_status_before_setup(local_tmp_path: Path) -> None:
    with _client(local_tmp_path) as client:
        response = client.get("/api/auth/status")

    assert response.status_code == 200
    assert response.json() == {
        "initialized": False,
        "authenticated": False,
        "vault_unlocked": False,
        "setup_required": True,
    }


def test_setup_initializes_unlocks_and_sets_http_only_cookie(local_tmp_path: Path) -> None:
    with _client(local_tmp_path) as client:
        response = client.post("/api/auth/setup", json={"passphrase": PASSPHRASE})

    assert response.status_code == 200
    body = response.json()
    assert body["initialized"] is True
    assert body["authenticated"] is True
    assert body["vault_unlocked"] is True
    assert body["setup_required"] is False
    assert "httponly" in response.headers["set-cookie"].lower()
    assert PASSPHRASE not in response.text


def test_duplicate_setup_is_rejected(local_tmp_path: Path) -> None:
    with _client(local_tmp_path) as client:
        assert client.post("/api/auth/setup", json={"passphrase": PASSPHRASE}).status_code == 200
        response = client.post("/api/auth/setup", json={"passphrase": PASSPHRASE})

    assert response.status_code == 409


def test_setup_rejects_weak_passphrase(local_tmp_path: Path) -> None:
    with _client(local_tmp_path) as client:
        response = client.post("/api/auth/setup", json={"passphrase": "too-short"})

    assert response.status_code == 400


def test_login_rejects_wrong_passphrase_and_accepts_correct_passphrase(local_tmp_path: Path) -> None:
    with _client(local_tmp_path) as client:
        assert client.post("/api/auth/setup", json={"passphrase": PASSPHRASE}).status_code == 200
        assert client.post("/api/auth/lock").status_code == 200

        wrong_response = client.post("/api/auth/login", json={"passphrase": "wrong horse battery staple"})
        correct_response = client.post("/api/auth/login", json={"passphrase": PASSPHRASE})

    assert wrong_response.status_code == 401
    assert correct_response.status_code == 200
    assert correct_response.json()["vault_unlocked"] is True
    assert PASSPHRASE not in correct_response.text


def test_logout_revokes_current_session(local_tmp_path: Path) -> None:
    with _client(local_tmp_path) as client:
        assert client.post("/api/auth/setup", json={"passphrase": PASSPHRASE}).status_code == 200
        logout_response = client.post("/api/auth/logout")
        status_response = client.get("/api/auth/status")

    assert logout_response.status_code == 200
    assert logout_response.json()["authenticated"] is False
    assert status_response.json()["authenticated"] is False


def test_lock_revokes_session_and_locks_vault(local_tmp_path: Path) -> None:
    with _client(local_tmp_path) as client:
        assert client.post("/api/auth/setup", json={"passphrase": PASSPHRASE}).status_code == 200
        lock_response = client.post("/api/auth/lock")
        status_response = client.get("/api/auth/status")

    assert lock_response.status_code == 200
    assert lock_response.json()["vault_unlocked"] is False
    assert status_response.json()["authenticated"] is False
    assert status_response.json()["vault_unlocked"] is False


def test_protected_auth_actions_require_valid_session(local_tmp_path: Path) -> None:
    with _client(local_tmp_path) as client:
        logout_response = client.post("/api/auth/logout")
        lock_response = client.post("/api/auth/lock")

    assert logout_response.status_code == 401
    assert lock_response.status_code == 401


def test_auth_api_responses_do_not_expose_session_token_or_secret_material(local_tmp_path: Path) -> None:
    with _client(local_tmp_path) as client:
        response = client.post("/api/auth/setup", json={"passphrase": PASSPHRASE})
        session_cookie = response.cookies.get("tablepro_session")
        runtime_response = client.get("/api/runtime")

    combined = f"{response.text} {runtime_response.text}".lower()
    assert session_cookie
    assert session_cookie.lower() not in combined
    assert PASSPHRASE not in combined
    assert "salt" not in combined
    assert "ciphertext" not in combined
