import typing

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine

from gyver.config import from_config
from gyver.database.typedef import Driver

from .config import DatabaseConfig
from .config import DefaultDatabaseConfig
from .context import AsyncSaAdapter
from .context import SaAdapter
from .utils import make_uri


class SyncDatabaseProvider(SaAdapter):
    def __init__(self, config: typing.Optional[DatabaseConfig] = None) -> None:
        self._config = config or from_config(DefaultDatabaseConfig)
        db_kwargs = (
            {}
            if self._config.driver is Driver.SQLITE
            else {
                "pool_size": self._config.pool_size,
                "pool_recycle": self._config.pool_recycle,
                "max_overflow": self._config.max_overflow,
            }
        )

        super().__init__(
            engine=sa.create_engine(make_uri(self.config, sync=True), **db_kwargs)
        )

    @property
    def config(self):
        return self._config


class AsyncDatabaseProvider(AsyncSaAdapter):
    def __init__(self, config: typing.Optional[DatabaseConfig] = None) -> None:
        self._config = config or from_config(DefaultDatabaseConfig)
        db_kwargs = (
            {}
            if self._config.driver is Driver.SQLITE
            else {
                "pool_size": self._config.pool_size,
                "pool_recycle": self._config.pool_recycle,
                "max_overflow": self._config.max_overflow,
            }
        )

        super().__init__(engine=create_async_engine(make_uri(self.config), **db_kwargs))

    @property
    def config(self):
        return self._config
