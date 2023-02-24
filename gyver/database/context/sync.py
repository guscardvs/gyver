import typing

import sqlalchemy as sa
import sqlalchemy.engine as sa_engine
import sqlalchemy.orm as sa_orm

from gyver import context
from gyver.utils import lazyfield

TransactionOption = typing.Optional[typing.Literal["open", "begin"]]

SaContext = context.Context[sa_engine.Connection]
SessionContext = context.Context[sa_orm.Session]


class SaAdapter(context.Adapter[sa_engine.Connection]):
    @typing.overload
    def __init__(
        self,
        *,
        uri: str,
        engine: None = None,
    ) -> None:
        ...

    @typing.overload
    def __init__(
        self,
        *,
        uri: None = None,
        engine: sa_engine.Engine,
    ) -> None:
        ...

    def __init__(
        self,
        *,
        uri: typing.Optional[str] = None,
        engine: typing.Optional[sa_engine.Engine] = None,
    ) -> None:
        if not any((uri, engine)):
            raise TypeError("Missing parameters (uri/engine)")
        self._uri = uri
        if engine is not None:
            self._engine = engine

    @lazyfield
    def _engine(self):
        assert self._uri
        return sa.create_engine(self._uri)

    def is_closed(self, client: sa_engine.Connection) -> bool:
        return client.closed

    def new(self):
        return self._engine.connect()

    def release(self, client: sa_engine.Connection) -> None:
        client.close()

    def begin(self, client: sa_engine.Connection) -> None:
        if client.in_transaction():
            client.begin_nested()
        else:
            client.begin()

    def commit(self, client: sa_engine.Connection) -> None:
        if trx := (client.get_nested_transaction() or client.get_transaction()):
            trx.commit()

    def rollback(self, client: sa_engine.Connection) -> None:
        if trx := (client.get_nested_transaction() or client.get_transaction()):
            trx.rollback()

    def in_atomic(self, client: sa_engine.Connection) -> bool:
        return client.in_transaction()

    def context(
        self,
    ) -> "SaContext":
        return SaContext(self)


class SessionAdapter(context.AtomicAdapter[sa_orm.Session]):
    def __init__(self, adapter: context.AtomicAdapter[sa_engine.Connection]) -> None:
        self._internal_adapter = adapter

    def new(self):
        return sa_orm.Session(self._internal_adapter.new())

    def release(self, client: sa_orm.Session) -> None:
        self._internal_adapter.release(client.get_bind())  # type: ignore

    def is_closed(self, client: sa_orm.Session) -> bool:
        # sqlalchemy session is never truly closed
        return self._internal_adapter.is_closed(client.get_bind())  # type: ignore

    def begin(self, client: sa_orm.Session) -> None:
        if client.in_transaction():
            client.begin_nested()
        else:
            client.begin()

    def commit(self, client: sa_orm.Session) -> None:
        if trx := (client.get_nested_transaction() or client.get_transaction()):
            trx.commit()

    def rollback(self, client: sa_orm.Session) -> None:
        if trx := (client.get_nested_transaction() or client.get_transaction()):
            trx.rollback()

    def in_atomic(self, client: sa_orm.Session) -> bool:
        return client.in_transaction()

    def context(
        self,
    ) -> "SessionContext":
        return SessionContext(self)
