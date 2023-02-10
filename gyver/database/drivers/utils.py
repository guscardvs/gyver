from gyver.database.drivers.dialect import DialectInfo
from gyver.database.typedef import Driver

from .interface import Dialect


def resolve_driver(driver: Driver) -> Dialect:
    _table: dict[Driver, Dialect] = {
        Driver.MYSQL: DialectInfo(
            default_port=3306,
            driver=Driver.MYSQL,
            dialect_name="mysql",
            async_driver="aiomysql",
            sync_driver="pymysql",
            only_host=False,
        ),
        Driver.POSTGRES: DialectInfo(
            default_port=5432,
            driver=Driver.POSTGRES,
            dialect_name="postgresql",
            async_driver="asyncpg",
            sync_driver="psycopg2",
            only_host=False,
        ),
        Driver.SQLITE: DialectInfo(
            default_port=0,
            driver=Driver.SQLITE,
            dialect_name="sqlite",
            async_driver="aiosqlite",
            sync_driver="",
            only_host=True,
        ),
        Driver.MARIADB: DialectInfo(
            default_port=3306,
            driver=Driver.MARIADB,
            dialect_name="mariadb",
            async_driver="aiomysql",
            sync_driver="pymysql",
            only_host=False,
        ),
    }
    return _table[driver]


def build_dialect_scheme(dialect: Dialect, sync: bool = False):
    return "+".join(
        item
        for item in (
            dialect.dialect_name,
            dialect.sync_driver if sync else dialect.async_driver,
        )
        if item
    )
