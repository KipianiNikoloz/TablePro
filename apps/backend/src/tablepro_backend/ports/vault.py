from __future__ import annotations

from typing import Protocol


class SecretVault(Protocol):
    def is_unlocked(self) -> bool:
        """Return whether the future encrypted vault is unlocked."""

    def resolve_secret_ref(self, secret_ref: str) -> str:
        """Resolve a future server-side secret reference to secret material."""
