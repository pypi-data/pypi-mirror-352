# tests/test_encryptors.py

from netcrypt.encryptors import AESCipher, FernetCipher
import os

def test_aes_cipher():
    key = os.urandom(32)
    cipher = AESCipher(key)
    plaintext = b"Test AES encryption"
    encrypted = cipher.encrypt(plaintext)
    decrypted = cipher.decrypt(encrypted)
    assert decrypted == plaintext

def test_fernet_cipher():
    cipher = FernetCipher()
    plaintext = b"Test Fernet encryption"
    encrypted = cipher.encrypt(plaintext)
    decrypted = cipher.decrypt(encrypted)
    assert decrypted == plaintext
