from gyver.config import as_config


@as_config
class CryptoConfig:
    __prefix__ = "crypto"

    secret: str
    spares: list[str]
