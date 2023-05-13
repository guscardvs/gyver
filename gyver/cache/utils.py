from gyver.url import URL
from gyver.url import Netloc

from .config import CacheConfig


def make_uri(config: CacheConfig) -> str:
    """
    The make_uri function creates a Redis URI from the given CacheConfig.

    :param config: CacheConfig: Pass the configuration to the function
    :return: A string that is a valid uri for connecting to redis
    """
    url = URL("")
    url.scheme = "redis"
    url.add(
        netloc_obj=Netloc("").set(
            config.host, config.user, config.password, config.port
        )
    )
    return url.encode()
