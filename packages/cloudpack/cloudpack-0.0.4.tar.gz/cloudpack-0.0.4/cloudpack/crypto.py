import os
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def derive_vault_key(
    password: str, salt: bytes, iterations=8, memory_cost=262144, lanes=4
) -> bytes:
    """
    Derive a 32-byte vault key from a password and salt using Argon2id.
    Requires a 16-byte salt and optional parameters for iterations, memory, and parallelism.
    """
    if len(salt) != 16:
        raise ValueError("Salt must be 16 bytes")

    kdf = Argon2id(
        iterations=iterations,
        memory_cost=memory_cost,
        lanes=lanes,
        length=32,
        salt=salt,
    )
    vault_key = kdf.derive(password.encode())
    return vault_key


def encrypt(data: bytes, key: bytes) -> bytes:
    """
    Encrypt data with AES-256-GCM using the provided 32-byte key.
    Generates a random 12-byte nonce and prepends it to the ciphertext.
    Returns nonce + encrypted data.
    """
    if len(key) != 32:
        raise ValueError("Key must be 32 bytes")

    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit nonce for AES-GCM
    encrypted = aesgcm.encrypt(nonce, data, associated_data=None)
    return nonce + encrypted  # nonce is prepended for use in decryption


def decrypt(encrypted_data: bytes, key: bytes) -> bytes:
    """
    Decrypt data encrypted with AES-256-GCM using the provided 32-byte key.
    Expects nonce prepended to encrypted data.
    Returns the original plaintext.
    """
    if len(key) != 32:
        raise ValueError("Key must be 32 bytes")
    if len(encrypted_data) < 13:  # nonce(12) + minimum 1 byte ciphertext
        raise ValueError("Encrypted data too short")

    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, associated_data=None)
