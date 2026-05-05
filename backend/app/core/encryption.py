"""
Encryption utilities for sensitive data at rest.
Uses Fernet symmetric encryption (AES-128-CBC with HMAC).
"""

import base64
import hashlib
from cryptography.fernet import Fernet
from app.core.config import settings


def _get_fernet_key() -> bytes:
    """
    Derive a Fernet-compatible key from SECRET_KEY.
    Fernet requires a 32-byte URL-safe base64-encoded key.
    """
    # Use SHA-256 to derive a consistent 32-byte key from SECRET_KEY
    key_bytes = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return base64.urlsafe_b64encode(key_bytes)


_fernet = Fernet(_get_fernet_key())


def encrypt_token(plaintext: str) -> str:
    """Encrypt a token/secret for storage in database."""
    if not plaintext:
        return ""
    return _fernet.encrypt(plaintext.encode()).decode()


def decrypt_token(ciphertext: str) -> str:
    """Decrypt a token/secret from database."""
    if not ciphertext:
        return ""
    try:
        return _fernet.decrypt(ciphertext.encode()).decode()
    except Exception:
        # If decryption fails (e.g., key changed), return empty
        # In production, this should be logged as a critical error
        return ""
