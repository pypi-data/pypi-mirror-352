from aia_protocol.pipeline.base_stage import PipelineStage
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64
import os

class EncryptionStage(PipelineStage):
    IV_SIZE = 12  # bytes
    TAG_LENGTH = 16  # bytes (128 bits)

    def __init__(self, base64_key: bytes):
        decoded_key = base64.b64decode(base64_key)
        if len(decoded_key) != 32:
            raise ValueError("Key must be 256 bits (32 bytes) after Base64 decoding.")
        self.key = decoded_key
        self.aesgcm = AESGCM(self.key)

    def processToSend(self, message: bytes) -> bytes:
        message = message or b""
        iv = os.urandom(self.IV_SIZE)
        ciphertext = self.aesgcm.encrypt(iv, message, associated_data=None)
        return iv + ciphertext  # Prepend IV for compatibility with Java

    def processToReceive(self, message: bytes) -> bytes:
        if not message or len(message) < self.IV_SIZE:
            raise ValueError("Invalid ciphertext")
        iv = message[:self.IV_SIZE]
        ciphertext = message[self.IV_SIZE:]
        return self.aesgcm.decrypt(iv, ciphertext, associated_data=None)

    @staticmethod
    def generate_key() -> str:
        """Generates a 256-bit AES key and returns it Base64-encoded."""
        return base64.b64encode(AESGCM.generate_key(bit_length=256)).decode()
