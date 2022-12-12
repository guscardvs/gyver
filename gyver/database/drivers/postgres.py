from gyver.database.typedef import Driver
from gyver.utils import frozen


@frozen
class PostgresDialect:
    default_port = 5432
    driver = Driver.POSTGRES
    dialect_name = "postgresql"
    async_driver = "asyncpg"
    sync_driver = "psycopg2"
    only_host = False
