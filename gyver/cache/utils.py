from urllib.parse import quote

from .config import CacheConfig


def make_uri(config: CacheConfig) -> str:
    """
    The make_uri function creates a Redis URI from the given CacheConfig.

    :param config: CacheConfig: Pass the configuration to the function
    :return: A string that is a valid uri for connecting to redis
    """
    return (
        (
            f"redis://{quote(config.user)}:{quote(config.password)}"
            f"@{config.host}:{config.port}/"
        )
        if all((config.user, config.password))
        else f"redis://{config.host}:{config.port}"
    )
