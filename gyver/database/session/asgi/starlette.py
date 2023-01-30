import typing

from starlette.applications import Starlette
from starlette.requests import Request

from gyver.database import AsyncSaContext
from gyver.database import SaContext
from gyver.database.config import DatabaseConfig
from gyver.database.provider import AsyncDatabaseProvider
from gyver.database.provider import SyncDatabaseProvider

TrxOptions = typing.Optional[typing.Literal["open", "begin"]]


def setup_database_session(
    app: Starlette,
    config: typing.Optional[DatabaseConfig] = None,
    sync: bool = False,
):
    provider_class = SyncDatabaseProvider if sync else AsyncDatabaseProvider

    def _setup():
        provider = provider_class(config)
        app.state.gyver_database = provider

    app.add_event_handler("startup", _setup)


def get_async_context(transaction_on: TrxOptions = "open"):
    def _get(request: Request) -> AsyncSaContext:
        provider = typing.cast(AsyncDatabaseProvider, request.app.state.gyver_database)
        return provider.context(transaction_on=transaction_on)

    return _get


def get_sync_context(transaction_on: TrxOptions = "open"):
    def _get(request: Request) -> SaContext:
        provider = typing.cast(SyncDatabaseProvider, request.app.state.gyver_database)
        return provider.context(transaction_on=transaction_on)

    return _get
