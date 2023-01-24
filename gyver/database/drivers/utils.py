from gyver.database.typedef import Driver

from .interface import Dialect
from .mysql import AsyncMyDialect
from .mysql import AsyncMyMariaDialect
from .postgres import PostgresDialect
from .sqlite import SqliteDriver


def resolve_driver(driver: Driver) -> Dialect:
    _table: dict[Driver, Dialect] = {
        Driver.MYSQL: AsyncMyDialect(),
        Driver.POSTGRES: PostgresDialect(),
        Driver.SQLITE: SqliteDriver(),
        Driver.MARIADB: AsyncMyMariaDialect(),
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
