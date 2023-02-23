from gyver.database.typedef import Driver
from gyver.utils import DeprecatedClass
from gyver.attrs import define


@define
class SqliteDriver(DeprecatedClass):
    default_port = 0
    driver = Driver.SQLITE
    dialect_name = "sqlite"
    async_driver = "aiosqlite"
    sync_driver = ""
    only_host = True
