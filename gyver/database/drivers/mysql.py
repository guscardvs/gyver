from gyver.database.typedef import Driver
from gyver.utils import frozen


@frozen
class MysqlDialect:
    default_port = 3306
    driver = Driver.MYSQL
    dialect_name = "mysql"
    async_driver = "aiomysql"
    sync_driver = "pymysql"
    only_host = False


class AsyncMyDialect(MysqlDialect):
    async_driver = "asyncmy"


class MariaDbDialect(MysqlDialect):
    dialect_name = "mariadb"


class AsyncMyMariaDialect(AsyncMyDialect, MariaDbDialect):
    pass
