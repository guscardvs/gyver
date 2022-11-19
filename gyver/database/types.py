from enum import Enum


class Driver(str, Enum):
    MYSQL = "mysql"
    POSTGRES = "postgres"
    SQLITE = "sqlite"


class OrderDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"
    DISABLED = "disabled"


class ClauseType(str, Enum):
    BIND = "bind"
    APPLY = "apply"
