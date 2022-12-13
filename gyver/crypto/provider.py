from .config import CryptoConfig
from gyver.config import from_config
from gyver.utils import lazyfield, make_singleton

from cryptography.fernet import MultiFernet, Fernet


@make_singleton
class CryptoProvider:
    def __init__(self, config: CryptoConfig | None = None) -> None:
        self._config = config or from_config(CryptoConfig)

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
