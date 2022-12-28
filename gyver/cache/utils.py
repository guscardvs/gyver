from urllib.parse import quote

from .config import CacheConfig


def make_uri(config: CacheConfig) -> str:
    return (
        (
            f"redis://{quote(config.user)}:{quote(config.password)}"
            f"@{config.host}:{config.port}/"
        )
        if all((config.user, config.password))
        else f"redis://{config.host}:{config.port}"
    )
