import os

from cloudpack.crypto import derive_vault_key, encrypt, decrypt


def test_encryption_roundtrip():
    password = "_V3ryStr0ngPa$$w0rd_!"
    salt = os.urandom(16)
    key = derive_vault_key(password, salt)
    message = b"test message"
    encrypted = encrypt(message, key)
    decrypted = decrypt(encrypted, key)
    assert decrypted == message
