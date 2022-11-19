from gyver.database.types import Driver
from gyver.utils import frozen


@frozen
class MysqlDialect:
    default_port = 3306
    driver = Driver.MYSQL
    dialect_name = "mysql"
    async_driver = "aiomysql"
    sync_driver = "pymysql"
    only_host = False
