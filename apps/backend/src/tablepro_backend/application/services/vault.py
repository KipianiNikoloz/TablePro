from __future__ import annotations

from tablepro_backend.ports.vault import SecretVault


class DeferredVaultService(SecretVault):
    """Boundary marker for the future encrypted vault implementation."""

    status = "deferred"

    def is_unlocked(self) -> bool:
        return False

    def resolve_secret_ref(self, secret_ref: str) -> str:
        raise NotImplementedError(
            "Vault unlock, encryption, and saved credentials are deferred to a future change."
        )
