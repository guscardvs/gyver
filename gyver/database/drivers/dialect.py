from gyver.attrs import define

from gyver.database.typedef import Driver


@define
class DialectInfo:
    default_port: int
    driver: Driver
    dialect_name: str
    async_driver: str
    sync_driver: str
    only_host: bool
