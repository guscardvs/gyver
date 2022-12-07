import typing

from typing_extensions import ParamSpec, Concatenate
import sqlalchemy as sa
from context_handler.ext.sqlalchemy import AsyncSaContext
from sqlalchemy.engine import Result

from gyver.exc import GyverError
from gyver.model import Model

from . import entity
from . import query


class AsyncServiceProvider(typing.Protocol):
    def context(self) -> AsyncSaContext:
        ...


EntityT_co = typing.TypeVar(
    "EntityT_co", bound=entity.AbstractEntity, covariant=True
)
ModelT_co = typing.TypeVar("ModelT_co", bound=Model, covariant=True)


R = typing.TypeVar("R")
P = ParamSpec("P")


class AlreadyReadResult(GyverError, IndexError):
    ...


class Response(typing.Generic[EntityT_co, ModelT_co]):
    def __init__(
        self,
        result: Result,
        converter: typing.Callable[[EntityT_co], ModelT_co],
    ) -> None:
        self._result = result
        self._converter = converter
        self._read = False

    @staticmethod
    def _prevalidate(
        func: typing.Callable[["Response"], R]
    ) -> typing.Callable[["Response"], R]:
        def _wrapper(self: "Response") -> R:
            if self._read:
                raise AlreadyReadResult()
            result = func(self)
            self._read = True
            return result

        return _wrapper

    @_prevalidate
    def first(self) -> typing.Optional[ModelT_co]:
        first = self._result.scalars().first()
        return first and self._converter(first)

    @_prevalidate
    def all(self) -> typing.Sequence[ModelT_co]:
        return tuple(
            self._converter(item) for item in self._result.scalars().all()
        )

    @_prevalidate
    def raw(self) -> Result:
        return self._result


class trx_wrapper(typing.Generic[P, R]):
    def __init__(
        self,
        func: typing.Callable[
            Concatenate["AsyncDatabaseService", P],
            typing.Coroutine[typing.Any, typing.Any, R],
        ],
    ) -> None:
        self._func = func

    async def __call__(
        self, funcself: "AsyncDatabaseService", *args: P.args, **kwds: P.kwargs
    ) -> R:
        return await self._func(funcself, *args, **kwds)

    async def commit(
        self, funcself: "AsyncDatabaseService", *args: P.args, **kwds: P.kwargs
    ) -> R:
        async with funcself._context.transaction_begin():
            return await self._func(funcself, *args, **kwds)


class AsyncDatabaseService(typing.Generic[EntityT_co, ModelT_co]):
    def __init__(
        self,
        entity_cls: type[EntityT_co],
        context: AsyncSaContext,
        converter: typing.Callable[[EntityT_co], ModelT_co],
    ) -> None:
        self._entity_cls = entity_cls
        self._context = context
        self._converter = converter

    async def select(
        self,
        *bind: query.BindClause,
        apply: typing.Sequence[query.ApplyClause] = (),
        q: typing.Optional[query.select] = None
    ) -> Response[EntityT_co, ModelT_co]:
        q = q or query.select(self._entity_cls)
        async with self._context.acquire_session() as session:
            result = await session.execute(q.bind(*bind).apply(*apply).get())
            return Response(result, self._converter)

    def _make_count(
        self, field: str
    ) -> typing.Callable[[query.Mapper], tuple[typing.Any]]:
        def _apply_count(ent: query.Mapper):
            return (sa.func.count(query.retrieve_attr(ent, field)),)

        return _apply_count

    async def count(self, field: str, *bind: query.BindClause) -> int:
        result = await self.select(
            *bind,
            q=query.select(
                self._entity_cls,
                self._make_count(field),
            )
        )
        return result.raw().scalar_one()

    @trx_wrapper
    async def create(self, payload: dict[str, typing.Any]):
        async with self._context.acquire_session() as session:
            obj = self._entity_cls(**payload)
            session.add(obj)
            await session.flush([obj])
            return self._converter(obj)
