from enum import Enum

class Driver(str, Enum):
    """Enum representing database drivers.

    Attributes:
        MYSQL (str): MySQL driver.
        POSTGRES (str): PostgreSQL driver.
        SQLITE (str): SQLite driver.
        MARIADB (str): MariaDB driver.
        CUSTOM (str): Custom driver.
    """
    MYSQL = "mysql"
    POSTGRES = "postgres"
    SQLITE = "sqlite"
    MARIADB = "mariadb"
    CUSTOM = "custom"

class OrderDirection(str, Enum):
    """Enum representing order directions.

    Attributes:
        ASC (str): Ascending order.
        DESC (str): Descending order.
        DISABLED (str): Disabled order.
    """
    ASC = "asc"
    DESC = "desc"
    DISABLED = "disabled"

class ClauseType(str, Enum):
    """Enum representing clause types.

    Attributes:
        BIND (str): Bind clause type.
        APPLY (str): Apply clause type.
    """
    BIND = "bind"
    APPLY = "apply"
