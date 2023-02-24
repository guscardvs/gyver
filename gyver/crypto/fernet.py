from typing import Optional

from cryptography.fernet import Fernet
from cryptography.fernet import MultiFernet

from gyver.config import AdapterConfigFactory
from gyver.utils import lazyfield

from .config import CryptoConfig


class FernetCryptoProvider:
    def __init__(self, config: Optional[CryptoConfig] = None) -> None:
        self._config = config or AdapterConfigFactory().load(CryptoConfig)

    @property
    def config(self):
        return self._config

    @lazyfield
    def _multi(self):
        f1 = Fernet(self._config.secret.encode("utf8"))
        fn = [Fernet(item.encode("utf8")) for item in self._config.spares]
        return MultiFernet([f1, *fn])

    def encrypt(self, secret: str) -> str:
        return self._multi.encrypt(secret.encode("utf8")).decode("utf8")

    def decrypt(self, digest: str) -> str:
        return self._multi.decrypt(digest.encode("utf8")).decode("utf8")
