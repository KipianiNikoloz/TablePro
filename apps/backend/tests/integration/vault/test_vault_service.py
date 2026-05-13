from __future__ import annotations

from pathlib import Path
import sqlite3

import pytest

from tablepro_backend.application.services.vault import VaultService
from tablepro_backend.core.config import Settings
from tablepro_backend.domain.auth import InvalidPassphraseError, VaultLockedError
from tablepro_backend.infrastructure.database.migrations import apply_app_migrations
from tablepro_backend.infrastructure.database.vault import SQLiteVaultRepository


def _vault_service(local_tmp_path: Path) -> VaultService:
    settings = Settings(
        data_dir=local_tmp_path,
        sqlite_path=local_tmp_path / "tablepro.sqlite3",
        vault_kdf_iterations=1000,
    )
    apply_app_migrations(settings)
    repository = SQLiteVaultRepository(settings)
    return VaultService(settings, repository)


def test_vault_stores_and_resolves_secret_refs(local_tmp_path: Path) -> None:
    service = _vault_service(local_tmp_path)
    service.initialize("correct horse battery staple")

    secret_ref = service.create_secret_ref("db-password", label="main", secret_type="database-password")

    assert secret_ref.startswith("sec_")
    assert service.resolve_secret_ref(secret_ref) == "db-password"


def test_secret_ref_data_is_persisted_encrypted(local_tmp_path: Path) -> None:
    service = _vault_service(local_tmp_path)
    service.initialize("correct horse battery staple")

    service.create_secret_ref("db-password")

    with sqlite3.connect(local_tmp_path / "tablepro.sqlite3") as connection:
        ciphertext = connection.execute("SELECT ciphertext FROM secret_refs").fetchone()[0]

    assert "db-password" not in ciphertext


def test_locked_vault_rejects_secret_resolution(local_tmp_path: Path) -> None:
    service = _vault_service(local_tmp_path)
    service.initialize("correct horse battery staple")
    secret_ref = service.create_secret_ref("db-password")
    service.lock()

    with pytest.raises(VaultLockedError):
        service.resolve_secret_ref(secret_ref)


def test_wrong_passphrase_does_not_unlock_vault(local_tmp_path: Path) -> None:
    service = _vault_service(local_tmp_path)
    service.initialize("correct horse battery staple")
    service.lock()

    with pytest.raises(InvalidPassphraseError):
        service.unlock("wrong horse battery staple")

    assert service.is_unlocked() is False
