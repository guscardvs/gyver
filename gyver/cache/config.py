from gyver.config import ProviderConfig


class CacheConfig(ProviderConfig):
    __prefix__ = "cache"

    host: str
    port: int = 6379
    user: str = ""
    password: str = ""
    max_connections: int = 10
    default_key_expiration: int = -1
