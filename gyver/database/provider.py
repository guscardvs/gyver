import typing

from context_handler.ext.sqlalchemy import AsyncSaAdapter
from context_handler.ext.sqlalchemy import SaAdapter

from gyver.config import from_config

from .config import DatabaseConfig
from .config import DefaultDatabaseConfig
from .utils import make_uri


class SyncDatabaseProvider(SaAdapter):
    def __init__(self, config: typing.Optional[DatabaseConfig] = None) -> None:
        self._config = config or from_config(DefaultDatabaseConfig)
        super().__init__(uri=make_uri(self.config, sync=True))

    @property
    def config(self):
        return self._config


class AsyncDatabaseProvider(AsyncSaAdapter):
    def __init__(self, config: typing.Optional[DatabaseConfig] = None) -> None:
        self._config = config or from_config(DefaultDatabaseConfig)
        super().__init__(uri=make_uri(self.config))

    @property
    def config(self):
        return self._config
