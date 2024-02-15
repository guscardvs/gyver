import typing
from datetime import date, time

import sqlalchemy as sa
from sqlalchemy.sql import Delete, Select, Update
from sqlalchemy.sql.elements import ColumnElement

from gyver.database.typedef import ClauseType

ExecutableType = typing.Union[Select, Update, Delete]
ExecutableT = typing.TypeVar("ExecutableT", bound=ExecutableType)
Sortable = typing.Union[int, float, date, time]
Comparison = ColumnElement[bool]  # type: ignore
FieldType = typing.Union[ColumnElement, sa.Column]
T = typing.TypeVar("T", contravariant=True)
Mapper = typing.Union[sa.Table, type]


class Comparator(typing.Protocol[T]):
    def __call__(self, field: FieldType, target: T) -> Comparison:
        ...


class Clause(typing.Protocol):
    type_: typing.ClassVar[ClauseType]


class BindClause(Clause, typing.Protocol):
    type_: typing.Literal[ClauseType.BIND]

    def bind(self, mapper: Mapper) -> Comparison:
        ...


class ApplyClause(Clause, typing.Protocol[ExecutableT]):
    type_: typing.Literal[ClauseType.APPLY]

    def apply(self, query: ExecutableT) -> ExecutableT:
        ...
