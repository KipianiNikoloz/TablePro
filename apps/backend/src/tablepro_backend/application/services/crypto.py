from __future__ import annotations

import base64
import secrets

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from tablepro_backend.domain.auth import InvalidPassphraseError

_VERIFIER_PLAINTEXT = "tablepro-vault-verifier-v1"


def generate_salt() -> bytes:
    return secrets.token_bytes(32)


def derive_fernet(passphrase: str, salt: bytes, iterations: int) -> Fernet:
    key = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
    ).derive(passphrase.encode("utf-8"))
    return Fernet(base64.urlsafe_b64encode(key))


def create_verifier(fernet: Fernet) -> str:
    return encrypt_text(fernet, _VERIFIER_PLAINTEXT)


def verify_passphrase(fernet: Fernet, verifier_ciphertext: str) -> None:
    try:
        verifier = decrypt_text(fernet, verifier_ciphertext)
    except InvalidPassphraseError:
        raise
    if verifier != _VERIFIER_PLAINTEXT:
        raise InvalidPassphraseError("Invalid passphrase.")


def encrypt_text(fernet: Fernet, value: str) -> str:
    return fernet.encrypt(value.encode("utf-8")).decode("ascii")


def decrypt_text(fernet: Fernet, ciphertext: str) -> str:
    try:
        return fernet.decrypt(ciphertext.encode("ascii")).decode("utf-8")
    except (InvalidToken, UnicodeDecodeError):
        raise InvalidPassphraseError("Unable to decrypt vault data.") from None
