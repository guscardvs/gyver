import typing
from dataclasses import dataclass

import sqlalchemy as sa
from gyver.database.types import ClauseType

from . import _helpers
from . import comp as cp
from . import interface
from .interface import BindClause
from .interface import Mapper

T = typing.TypeVar("T")


@dataclass
class Where(typing.Generic[T]):
    type_ = ClauseType.BIND
    field: str
    expected: typing.Optional[T] = None
    comp: interface.Comparator[T] = cp.equals

    def bind(self, mapper: Mapper) -> interface.Comparison:
        attr = _helpers.retrieve_attr(mapper, self.field)
        return (
            sa.true()
            if self.expected is None
            else self.comp(attr, self.expected)
        )


@dataclass(frozen=True)
class _JoinBind:
    type_ = ClauseType.BIND
    items: typing.Sequence[BindClause]
    operator: typing.Callable[..., interface.Comparison]

    def bind(self, mapper: Mapper) -> interface.Comparison:
        return self.operator(*(item.bind(mapper) for item in self.items))


def and_(*bind: BindClause) -> _JoinBind:
    return _JoinBind(bind, sa.and_)


def or_(*bind: BindClause) -> _JoinBind:
    return _JoinBind(bind, sa.or_)
