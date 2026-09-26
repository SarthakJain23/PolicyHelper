import base64
import hashlib
from typing import Self
from cryptography.fernet import Fernet
from app.core.config import settings


class CryptoService:
    """
    Singleton Service for encrypting and decrypting API keys and secrets at rest.
    Uses Fernet (AES-128-CBC + HMAC-SHA256 authenticated encryption).
    """

    _instance: "CryptoService | None" = None
    _fernet: Fernet | None = None

    def __new__(cls) -> "CryptoService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    @classmethod
    def get_instance(cls) -> "CryptoService":
        """Return the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _initialize(self) -> None:
        """Derive 32-byte urlsafe base64 key from JWT_SECRET_KEY and instantiate Fernet."""
        secret = settings.JWT_SECRET_KEY
        derived_bytes = hashlib.sha256(secret.encode("utf-8")).digest()
        key = base64.urlsafe_b64encode(derived_bytes)
        self._fernet = Fernet(key)

    def encrypt(self, plain_text: str) -> str:
        """Encrypt plaintext secret for storage at rest."""
        if not plain_text:
            return ""
        if not self._fernet:
            self._initialize()
        return self._fernet.encrypt(plain_text.encode("utf-8")).decode("utf-8")

    def decrypt(self, encrypted_text: str) -> str:
        """Decrypt ciphertext secret back to plaintext."""
        if not encrypted_text:
            return ""
        if not self._fernet:
            self._initialize()
        try:
            return self._fernet.decrypt(encrypted_text.encode("utf-8")).decode("utf-8")
        except Exception:
            return ""

    def mask(self, plain_text: str) -> str:
        """Generate a secure fingerprint mask for UI display (e.g. sk-proj-...4X9z)."""
        if not plain_text:
            return ""
        if len(plain_text) <= 8:
            return "****"
        return f"{plain_text[:6]}...{plain_text[-4:]}"


# Global convenience helper methods delegate to the Singleton instance
def encrypt_api_key(plain_key: str) -> str:
    return CryptoService.get_instance().encrypt(plain_key)


def decrypt_api_key(encrypted_key: str) -> str:
    return CryptoService.get_instance().decrypt(encrypted_key)


def mask_api_key(api_key: str) -> str:
    return CryptoService.get_instance().mask(api_key)

