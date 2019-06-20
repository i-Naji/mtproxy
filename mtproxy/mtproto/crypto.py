from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class AES:
    """Core Crypto class by cryptography cipher

    Args:
        cipher (:class:`cryptography.hazmat.primitives.ciphers.Cipher`)
    """
    def __init__(self, cipher: Cipher):
        self.encryptor = cipher.encryptor()
        self.decryptor = cipher.decryptor()

    def encrypt(self, data: bytes) -> bytes:
        """Encryption method

        Args:
            data (``bytes``)
            data for encrypting

        Return:
            ``bytes``: encrypted data
        """
        return self.encryptor.update(data)

    def decrypt(self, data: bytes) -> bytes:
        """Decryption method

        Args:
            data (``bytes``)
                encrypted data

        Return:
            ``bytes``: decrypted data
        """
        return self.decryptor.update(data)

    @classmethod
    def create_aes_ctr(cls, key: bytes, iv: int) -> 'AES':
        """Create AES algorithm CRT mode Crypto with cryptography library

        Args:
            key (``bytes``)
                Encryption/Decryption Core key
            iv (``int``)
                Encryption/Decryption Counter key
        Return:
            :class:`AES`: if key and iv be correct and suitable
        """
        cipher = Cipher(algorithms.AES(key), modes.CTR(int.to_bytes(iv, 16, 'big')), default_backend())
        return cls(cipher)
