from __future__ import annotations

import pytest

from tablepro_backend.application.services.crypto import (
    create_verifier,
    decrypt_text,
    derive_fernet,
    encrypt_text,
    generate_salt,
    verify_passphrase,
)
from tablepro_backend.domain.auth import InvalidPassphraseError


def test_fernet_key_encrypts_and_decrypts_secret_text() -> None:
    fernet = derive_fernet("correct horse battery staple", generate_salt(), 1000)

    ciphertext = encrypt_text(fernet, "db-password")

    assert ciphertext != "db-password"
    assert decrypt_text(fernet, ciphertext) == "db-password"


def test_verifier_rejects_wrong_passphrase() -> None:
    salt = generate_salt()
    verifier = create_verifier(derive_fernet("correct horse battery staple", salt, 1000))
    wrong_key = derive_fernet("wrong horse battery staple", salt, 1000)

    with pytest.raises(InvalidPassphraseError):
        verify_passphrase(wrong_key, verifier)
