from typing import ClassVar
from typing import Protocol

from gyver.database.types import Driver


class Dialect(Protocol):
    default_port: ClassVar[int]
    driver: ClassVar[Driver]
    dialect_name: ClassVar[str]
    async_driver: ClassVar[str]
    sync_driver: ClassVar[str]
    only_host: ClassVar[bool]
