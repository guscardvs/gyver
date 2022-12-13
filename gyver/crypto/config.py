from gyver.config import ProviderConfig


class CryptoConfig(ProviderConfig):
    __prefix__ = "crypto"

    secret: str
    spares: list[str]
