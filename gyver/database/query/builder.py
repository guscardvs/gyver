import typing

import sqlalchemy as sa
from sqlalchemy.sql import Delete
from sqlalchemy.sql import Select
from sqlalchemy.sql import Update

from gyver.utils import lazyfield

from . import _helpers
from ._helpers import retrieve_attr
from .interface import ApplyClause
from .interface import BindClause
from .interface import Mapper

ExecutableType = typing.Union[Select, Update, Delete]
ExecutableT = typing.TypeVar("ExecutableT", bound=ExecutableType)
Self = typing.TypeVar("Self", bound="Query")


class Query(typing.Generic[ExecutableT]):
    def __init__(
        self,
        entity: Mapper,
        executable: typing.Callable[..., ExecutableT],
    ) -> None:
        self._entity = entity
        self._executable = executable

    def _preprocess_params(self, entity: Mapper) -> typing.Sequence[typing.Any]:
        return (entity,)

    def _process_query(self, query: ExecutableT) -> ExecutableT:
        return query

    @lazyfield
    def query(self):
        return self._process_query(
            self._executable(*self._preprocess_params(self._entity))
        )

    def bind(self: Self, *where: BindClause) -> Self:
        self.query = _process_filters(self.query, self._entity, where)
        return self

    def get(self):
        return self.query


class select(Query[Select]):
    def __init__(
        self,
        entity: Mapper,
        apply_func: typing.Optional[
            typing.Callable[[Mapper], tuple[typing.Any, ...]]
        ] = None,
    ) -> None:
        super().__init__(entity, sa.select)
        self._apply_func = apply_func or self._default_apply

    @staticmethod
    def _default_apply(entity: Mapper) -> tuple[Mapper]:
        return (entity,)

    def _preprocess_params(self, entity: Mapper) -> typing.Sequence[typing.Any]:
        return self._apply_func(entity)

    def apply(self: Self, *clauses: ApplyClause) -> Self:
        for item in clauses:
            self.query = item.apply(self.query)
        return self


class update(Query[Update]):
    def __init__(self, entity: Mapper, values: typing.Mapping[str, typing.Any]) -> None:
        super().__init__(entity, sa.update)
        self._values = values

    def _process_query(self, query: Update) -> Update:
        return query.values(self._values)


class delete(Query[Delete]):
    def __init__(self, entity: Mapper) -> None:
        super().__init__(entity, sa.delete)


def count(entity: Mapper, field: str = "id"):
    def _make_count(entity: Mapper):
        return (sa.func.count(retrieve_attr(entity, field)),)

    return select(entity, _make_count)


def distinct(entity: Mapper, *fields: str):
    def _make_distinct(ent: Mapper):
        return tuple(_helpers.retrieve_attr(ent, field).distinct() for field in fields)

    return select(entity, _make_distinct)


def _process_filters(
    query: ExecutableType, entity: Mapper, where: typing.Sequence
) -> ExecutableType:
    return query.where(*(clause.bind(entity) for clause in where))
