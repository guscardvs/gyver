import typing

from gyver.database import AsyncSaContext
from gyver.database import SaContext
from sanic import Request
from sanic import Sanic

from gyver.database.config import DatabaseConfig
from gyver.database.provider import AsyncDatabaseProvider
from gyver.database.provider import SyncDatabaseProvider

TrxOptions = typing.Optional[typing.Literal["open", "begin"]]


def setup_database_session(
    app: Sanic,
    config: typing.Optional[DatabaseConfig] = None,
    sync: bool = False,
):
    provider_class = SyncDatabaseProvider if sync else AsyncDatabaseProvider

    async def _setup(_):
        provider = provider_class(config)
        app.ctx.gyver_database = provider

    app.register_listener(_setup, "before_server_start")


def get_async_context(transaction_on: TrxOptions = "open"):
    def _get(request: Request) -> AsyncSaContext:
        provider = typing.cast(
            AsyncDatabaseProvider, request.app.ctx.gyver_database
        )
        return provider.context(transaction_on=transaction_on)

    return _get


def get_sync_context(transaction_on: TrxOptions = "open"):
    def _get(request: Request) -> SaContext:
        provider = typing.cast(
            SyncDatabaseProvider, request.app.ctx.gyver_database
        )
        return provider.context(transaction_on=transaction_on)

    return _get
