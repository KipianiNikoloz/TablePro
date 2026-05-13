from __future__ import annotations

from dataclasses import dataclass

from tablepro_backend.application.services.vault import VaultService
from tablepro_backend.core.config import Settings
from tablepro_backend.domain.auth import SessionInvalidError
from tablepro_backend.infrastructure.database.vault import SQLiteVaultRepository


@dataclass(frozen=True)
class AuthStatus:
    initialized: bool
    authenticated: bool
    vault_unlocked: bool

    @property
    def setup_required(self) -> bool:
        return not self.initialized


@dataclass(frozen=True)
class AuthSession:
    token: str


class AuthService:
    def __init__(
        self,
        settings: Settings,
        repository: SQLiteVaultRepository,
        vault: VaultService,
    ) -> None:
        self.settings = settings
        self.repository = repository
        self.vault = vault

    def status(self, session_token: str | None) -> AuthStatus:
        initialized = self.repository.vault_state_exists()
        authenticated = False
        if session_token:
            authenticated = (
                self.repository.validate_session(
                    session_token,
                    self.settings.auth_session_idle_timeout_seconds,
                )
                is not None
            )
        return AuthStatus(
            initialized=initialized,
            authenticated=authenticated,
            vault_unlocked=self.vault.is_unlocked(),
        )

    def setup(self, passphrase: str) -> AuthSession:
        self.vault.initialize(passphrase)
        return self._create_session()

    def login(self, passphrase: str) -> AuthSession:
        self.vault.unlock(passphrase)
        return self._create_session()

    def logout(self, session_token: str | None) -> None:
        token = self.require_session(session_token)
        self.repository.revoke_session(token)

    def lock(self, session_token: str | None) -> None:
        self.require_session(session_token)
        self.vault.lock()
        self.repository.revoke_all_sessions()

    def require_session(self, session_token: str | None) -> str:
        if not session_token:
            raise SessionInvalidError("Authentication session is required.")
        validation = self.repository.validate_session(
            session_token,
            self.settings.auth_session_idle_timeout_seconds,
        )
        if validation is None:
            raise SessionInvalidError("Authentication session is invalid or expired.")
        return validation.token

    def _create_session(self) -> AuthSession:
        return AuthSession(
            token=self.repository.create_session(self.settings.auth_session_idle_timeout_seconds)
        )
