from types import FunctionType
from typing import Any
from typing import Optional
from typing import Sequence
from typing import Union

from gyver import utils
from gyver.config import ProviderConfig
from gyver.exc import InvalidField
from gyver.utils.exc import panic

from . import drivers
from .typedef import Driver


class ConnectionPoolConfig(ProviderConfig):

    """
    A configuration object for a connection pool.
    """

    pool_size: int = 20
    """
    The maximum number of connections to keep in the pool.
    """

    pool_recycle: int = 3600
    """
    The number of seconds to keep a connection alive, after which it will be closed and replaced.
    """

    max_overflow: int = 0
    """
    The maximum number of connections to allow above the pool_size, or None to disable overflow.
    """


class DatabaseConfig(ProviderConfig):
    driver: Driver
    host: str
    port: int = -1
    user: str = ""
    password: str = ""
    name: str = ""
    pool_size: int = 20
    pool_recycle: int = 3600
    max_overflow: int = 0

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
        self.dialect = dialect
        self.dialect_overriden = True


def make_database_config(
    prefix: str,
    without_prefix: Sequence[str] = (),
    name: str = "DatabaseConfig",
    module: Optional[str] = __name__,
    **defaults: Union[Any, FunctionType],
) -> type[DatabaseConfig]:  # sourcery skip: instance-method-first-arg-name
    new_cls = type(
        name,
        (DatabaseConfig,),
        {
            "__prefix__": prefix,
            "__without_prefix__": without_prefix,
            "__module__": module,
        },
    )
    for key, value in defaults.items():
        _override_defaults(new_cls, key, value)
    return new_cls


def _override_defaults(
    new_cls: type[DatabaseConfig], key: str, value: Union[Any, FunctionType]
):
    try:
        modelfield = new_cls.__fields__[key]
    except KeyError:
        raise panic(
            InvalidField,
            f"Field {key} not found in model {new_cls.__name__}",
        ) from None
    else:
        if isinstance(value, FunctionType):
            modelfield.default_factory = value
        else:
            modelfield.default


DefaultDatabaseConfig = make_database_config("db")
