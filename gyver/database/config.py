from typing import Optional
from typing import Sequence

from gyver import utils
from gyver.config import ProviderConfig

from . import drivers
from .types import Driver


class DatabaseConfig(ProviderConfig):
    driver: Driver
    host: str
    port: int = -1
    user: str = ""
    password: str = ""
    name: str = ""

    @utils.lazyfield
    def real_port(self) -> int:
        return self.port if self.port != -1 else self.dialect.default_port

    @utils.lazyfield
    def dialect(self) -> drivers.Dialect:
        return drivers.resolve_driver(self.driver)


def make_database_config(
    prefix: str,
    without_prefix: Sequence[str] = (),
    name: str = "DatabaseConfig",
    module: Optional[str] = __name__,
) -> type[DatabaseConfig]:
    return type(
        name,
        (DatabaseConfig,),
        {
            "__prefix__": prefix,
            "__without_prefix__": without_prefix,
            "__module__": module,
        },
    )


DefaultDatabaseConfig = make_database_config("db")
