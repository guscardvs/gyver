from gyver import utils
from gyver.config import as_config
from gyver.exc import InvalidField
from gyver.utils.exc import panic
from gyver.utils.lazy import setlazy

from . import drivers
from .typedef import Driver


@as_config
class DatabaseConfig:
    driver: Driver
    host: str
    port: int = -1
    user: str = ""
    password: str = ""
    name: str = ""
    pool_size: int = 20
    pool_recycle: int = 3600
    max_overflow: int = 0
    autotransaction: bool = False

    @utils.lazyfield
    def effective_port(self) -> int:
        return self.port if self.port != -1 else self.dialect.default_port

    @utils.lazyfield
    def dialect(self) -> drivers.Dialect:
        if self.driver is Driver.CUSTOM and not self.dialect_overriden:
            raise panic(
                InvalidField,
                'Field driver of value "custom" missing custom dialect,'
                "dont forget to call .override_dialect(dialect)",
            )
        return drivers.resolve_driver(self.driver)

    @utils.lazyfield
    def dialect_overriden(self):
        return False

    def override_dialect(self, dialect: drivers.Dialect) -> None:
        setlazy(self, "dialect", dialect, bypass_setattr=True)
        setlazy(self, "dialect_overriden", True, bypass_setattr=True)
