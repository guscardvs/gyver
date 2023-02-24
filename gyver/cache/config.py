from gyver.config import as_config


@as_config
class CacheConfig:
    __prefix__ = "cache"

    host: str
    port: int = 6379
    user: str = ""
    password: str = ""
    max_connections: int = 10
    default_key_expiration: int = -1
