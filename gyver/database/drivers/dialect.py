from gyver.attrs import define
from gyver.database.typedef import Driver

@define
class DialectInfo:
    """Represents information about a database dialect.

    Attributes:
        default_port (int): The default port for the database dialect.
        driver (Driver): The driver associated with the dialect.
        dialect_name (str): The name of the database dialect.
        async_driver (str): The asynchronous driver name.
        sync_driver (str): The synchronous driver name.
        only_host (bool): Indicates if the dialect supports only host connections.
    """
    default_port: int
    driver: Driver
    dialect_name: str
    async_driver: str
    sync_driver: str
    only_host: bool