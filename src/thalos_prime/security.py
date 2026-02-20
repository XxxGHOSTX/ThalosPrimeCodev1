"""Security primitives for the Thalos Prime prototype."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Dict

from .thalos_sbi_core import CryptoManager


@dataclass
class AccessPolicy:
    allow_parameter_export: bool = False


class HashVerifier:
    """Simple SHA256 verifier for prototype assets."""

    @staticmethod
    def digest(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def verify(data: bytes, expected: str) -> bool:
        return HashVerifier.digest(data) == expected


class EncryptionService:
    """Wrapper around CryptoManager for simple usage."""

    def __init__(self, passphrase: str) -> None:
        self.crypto = CryptoManager(passphrase)

    def encrypt_text(self, text: str) -> str:
        payload = text.encode("utf-8")
        encrypted = self.crypto.encrypt(payload)
        return encrypted.hex()

    def decrypt_text(self, payload_hex: str) -> str:
        payload = bytes.fromhex(payload_hex)
        decrypted = self.crypto.decrypt(payload)
        return decrypted.decode("utf-8")


class ParameterVault:
    """Stores encrypted parameters in memory with access control."""

    def __init__(self, policy: AccessPolicy, encryption: EncryptionService) -> None:
        self.policy = policy
        self.encryption = encryption
        self._store: Dict[str, str] = {}

    def put(self, name: str, payload: str) -> None:
        self._store[name] = self.encryption.encrypt_text(payload)

    def get(self, name: str) -> str:
        if not self.policy.allow_parameter_export:
            raise PermissionError("Parameter export disabled by policy")
        encrypted = self._store[name]
        return self.encryption.decrypt_text(encrypted)
