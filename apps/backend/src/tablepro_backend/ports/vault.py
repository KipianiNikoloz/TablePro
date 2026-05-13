from __future__ import annotations

from typing import Protocol


class SecretVault(Protocol):
    def is_unlocked(self) -> bool:
        """Return whether decrypted vault key material is available."""

    def resolve_secret_ref(self, secret_ref: str) -> str:
        """Resolve a server-side secret reference to secret material."""

    def create_secret_ref(
        self,
        secret_value: str,
        *,
        label: str | None = None,
        secret_type: str = "generic",
    ) -> str:
        """Store secret material and return an opaque server-side reference."""

    def update_secret_ref(self, secret_ref: str, secret_value: str) -> None:
        """Replace secret material for an existing reference."""

    def delete_secret_ref(self, secret_ref: str) -> None:
        """Delete a server-side secret reference."""
