from gyver.database.typedef import Driver
from gyver.utils import frozen


@frozen
class SqliteDriver:
    default_port = 0
    driver = Driver.SQLITE
    dialect_name = "sqlite"
    async_driver = "aiosqlite"
    sync_driver = ""
    only_host = True
