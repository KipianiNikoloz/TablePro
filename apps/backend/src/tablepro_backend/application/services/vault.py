from __future__ import annotations

from dataclasses import dataclass

from cryptography.fernet import Fernet

from tablepro_backend.application.services.crypto import (
    create_verifier,
    decrypt_text,
    derive_fernet,
    encrypt_text,
    generate_salt,
    verify_passphrase,
)
from tablepro_backend.core.config import Settings
from tablepro_backend.domain.auth import (
    InvalidPassphraseError,
    VaultAlreadyInitializedError,
    VaultLockedError,
    VaultNotInitializedError,
)
from tablepro_backend.infrastructure.database.vault import SQLiteVaultRepository
from tablepro_backend.ports.vault import SecretVault


@dataclass(frozen=True)
class VaultStatus:
    initialized: bool
    unlocked: bool

    @property
    def status(self) -> str:
        if not self.initialized:
            return "uninitialized"
        if self.unlocked:
            return "unlocked"
        return "locked"


class VaultService(SecretVault):
    def __init__(self, settings: Settings, repository: SQLiteVaultRepository) -> None:
        self.settings = settings
        self.repository = repository
        self._fernet: Fernet | None = None

    def status(self) -> VaultStatus:
        return VaultStatus(
            initialized=self.repository.vault_state_exists(),
            unlocked=self.is_unlocked(),
        )

    def is_unlocked(self) -> bool:
        return self._fernet is not None

    def initialize(self, passphrase: str) -> None:
        self._validate_passphrase_strength(passphrase)
        if self.repository.vault_state_exists():
            raise VaultAlreadyInitializedError("Vault is already initialized.")
        salt = generate_salt()
        fernet = derive_fernet(passphrase, salt, self.settings.vault_kdf_iterations)
        self.repository.initialize_vault(
            kdf_algorithm=self.settings.vault_kdf_algorithm,
            kdf_iterations=self.settings.vault_kdf_iterations,
            salt=salt,
            verifier_ciphertext=create_verifier(fernet),
        )
        self._fernet = fernet

    def unlock(self, passphrase: str) -> None:
        state = self.repository.load_vault_state()
        if state is None:
            raise VaultNotInitializedError("Vault has not been initialized.")
        if state.kdf_algorithm != self.settings.vault_kdf_algorithm:
            raise InvalidPassphraseError("Unsupported vault key derivation metadata.")
        fernet = derive_fernet(passphrase, state.salt, state.kdf_iterations)
        verify_passphrase(fernet, state.verifier_ciphertext)
        self._fernet = fernet

    def lock(self) -> None:
        self._fernet = None

    def create_secret_ref(
        self,
        secret_value: str,
        *,
        label: str | None = None,
        secret_type: str = "generic",
    ) -> str:
        fernet = self._require_unlocked()
        record = self.repository.create_secret_ref(
            ciphertext=encrypt_text(fernet, secret_value),
            label=label,
            secret_type=secret_type,
        )
        return record.id

    def resolve_secret_ref(self, secret_ref: str) -> str:
        fernet = self._require_unlocked()
        record = self.repository.load_secret_ref(secret_ref)
        return decrypt_text(fernet, record.ciphertext)

    def update_secret_ref(self, secret_ref: str, secret_value: str) -> None:
        fernet = self._require_unlocked()
        self.repository.update_secret_ref(secret_ref, encrypt_text(fernet, secret_value))

    def delete_secret_ref(self, secret_ref: str) -> None:
        self.repository.delete_secret_ref(secret_ref)

    def _require_unlocked(self) -> Fernet:
        if self._fernet is None:
            raise VaultLockedError("Vault is locked.")
        return self._fernet

    def _validate_passphrase_strength(self, passphrase: str) -> None:
        if len(passphrase) < self.settings.vault_passphrase_min_length:
            raise InvalidPassphraseError(
                f"Passphrase must be at least {self.settings.vault_passphrase_min_length} characters."
            )
