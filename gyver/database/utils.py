from urllib.parse import quote

from gyver.utils import cache

from . import drivers
from .config import DatabaseConfig


@cache
def make_uri(config: DatabaseConfig, sync: bool = False) -> str:
    if config.dialect.only_host:
        return f"{drivers.build_dialect_scheme(config.dialect, sync)}://{config.host}"
    return (
        f"{drivers.build_dialect_scheme(config.dialect, sync)}://"
        f"{quote(config.user)}:{quote(config.password)}@"
        f"{config.host}:{config.real_port}/"
        f"{quote(config.name)}"
    )
