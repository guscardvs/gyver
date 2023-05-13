import typing

import sqlalchemy as sa
from gyver.attrs import define
from gyver.attrs import info
from sqlalchemy.ext.asyncio import create_async_engine

from gyver.config import AdapterConfigFactory
from gyver.context import atomic
from gyver.database.context.asyncio import AsyncSessionAdapter
from gyver.database.context.sync import SessionAdapter
from gyver.database.typedef import Driver
from gyver.utils.lazy import lazyfield

from .config import DatabaseConfig
from .context import AsyncConnectionAdapter
from .context import SaAdapter
from .utils import make_uri

db_config_loader = AdapterConfigFactory().maker(DatabaseConfig, "db")


@define
class DatabaseAdapter:
    config: DatabaseConfig = info(default=db_config_loader)
    db_kwargs: dict[str, typing.Any] = info(default_factory=dict)

    def __post_init__(self) -> None:
        if self.config.driver is not Driver.SQLITE:
            self.db_kwargs.update(
                {
                    "pool_size": self.config.pool_size,
                    "pool_recycle": self.config.pool_recycle,
                    "max_overflow": self.config.max_overflow,
                }
            )

    @lazyfield
    def async_engine(self):
        return create_async_engine(make_uri(self.config), **self.db_kwargs)

    @lazyfield
    def engine(self):
        return sa.create_engine(make_uri(self.config, sync=True), **self.db_kwargs)

    def context(self):
        context = SaAdapter(engine=self.engine).context()
        return atomic(context) if self.config.autotransaction else context

    def async_context(self):
        context = AsyncConnectionAdapter(engine=self.async_engine).context()
        return atomic(context) if self.config.autotransaction else context

    def session(self):
        context = SessionAdapter(SaAdapter(engine=self.engine)).context()
        return atomic(context) if self.config.autotransaction else context

    def async_session(self):
        context = AsyncSessionAdapter(
            AsyncConnectionAdapter(engine=self.async_engine)
        ).context()
        return atomic(context) if self.config.autotransaction else context
