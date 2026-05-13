from __future__ import annotations


class AuthError(Exception):
    """Base class for local auth/vault errors."""


class InvalidPassphraseError(AuthError):
    """Raised when a submitted passphrase is wrong or too weak."""


class SessionInvalidError(AuthError):
    """Raised when an auth session is missing, expired, or revoked."""


class VaultAlreadyInitializedError(AuthError):
    """Raised when setup is attempted after vault initialization."""


class VaultNotInitializedError(AuthError):
    """Raised when login or secret operations require setup first."""


class VaultLockedError(AuthError):
    """Raised when decrypted vault key material is not available."""


class SecretRefNotFoundError(AuthError):
    """Raised when a secret reference cannot be found."""
