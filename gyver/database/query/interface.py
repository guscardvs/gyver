import typing
from datetime import date
from datetime import time

import sqlalchemy as sa
from sqlalchemy.sql import Delete
from sqlalchemy.sql import Select
from sqlalchemy.sql import Update
from sqlalchemy.sql.elements import BooleanClauseList
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.functions import Function

from gyver.database.entity import AbstractEntity
from gyver.database.typedef import ClauseType

ExecutableType = typing.Union[Select, Update, Delete]
ExecutableT = typing.TypeVar("ExecutableT", bound=ExecutableType)
Sortable = typing.Union[int, float, date, time]
Comparison = typing.Union[ColumnElement[sa.Boolean], BooleanClauseList, Function]
FieldType = typing.Union[ColumnElement, sa.Column]
T = typing.TypeVar("T", contravariant=True)
Mapper = typing.Union[sa.Table, type[AbstractEntity]]


class Comparator(typing.Protocol[T]):
    def __call__(self, field: FieldType, target: T) -> typing.Any:
        pass


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
