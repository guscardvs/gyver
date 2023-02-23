from gyver.database.typedef import Driver
from gyver.utils import DeprecatedClass
from gyver.attrs import define


@define
class PostgresDialect(DeprecatedClass):
    default_port = 5432
    driver = Driver.POSTGRES
    dialect_name = "postgresql"
    async_driver = "asyncpg"
    sync_driver = "psycopg2"
    only_host = False
