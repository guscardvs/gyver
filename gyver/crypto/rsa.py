from typing import Optional

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa

from gyver.config import ConfigLoader
from gyver.config import ProviderConfig
from gyver.utils import lazyfield


class RSACryptoConfig(ProviderConfig):
    __prefix__ = "crypto"

    private_key: str
    public_key: str


class RSACryptoProvider:
    def __init__(self, config: Optional[RSACryptoConfig] = None) -> None:
        self._config = config or ConfigLoader().load(RSACryptoConfig)

    @property
    def config(self):
        return self._config

    @lazyfield
    def _private_key(self) -> rsa.RSAPrivateKey:
        return serialization.load_pem_private_key(  # type: ignore
            self._config.private_key.encode(),
            password=None,
            backend=default_backend(),
        )

    @lazyfield
    def _public_key(self) -> rsa.RSAPublicKey:
        return serialization.load_pem_public_key(  # type:ignore
            self._config.public_key.encode(), backend=default_backend()
        )

    def encrypt(self, secret: str) -> str:
        ciphertext = self._public_key.encrypt(
            secret.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return ciphertext.hex()

    def decrypt(self, ciphertext: str) -> str:
        encoded = bytes.fromhex(ciphertext)
        return self._private_key.decrypt(
            encoded,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        ).decode()
