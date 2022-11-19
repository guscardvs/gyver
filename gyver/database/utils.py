from urllib.parse import quote

from gyver.utils import cache

from . import drivers
from .config import DatabaseConfig


@cache
def make_uri(config: DatabaseConfig, sync: bool = False) -> str:
    base_uri = (
        f"{drivers.build_dialect_scheme(config.dialect, sync)}://{config.host}"
    )
    if config.dialect.only_host:
        return base_uri
    return (
        f"{base_uri}:{config.real_port}@"
        f"{quote(config.user)}:{quote(config.password)}/"
        f"{quote(config.name)}"
    )
