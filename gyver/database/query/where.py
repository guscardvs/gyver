import typing
from dataclasses import dataclass

import sqlalchemy as sa

from . import _helpers
from . import comp as cp
from . import interface
from .interface import BindClause
from .interface import Mapper

T = typing.TypeVar("T")


@dataclass
class Where(typing.Generic[T]):
    field: str
    expected: typing.Optional[T] = None
    comp: interface.Comparator[T] = cp.equals

    def bind(self, entity: Mapper) -> interface.Comparison:
        attr = _helpers.retrieve_attr(entity, self.field)
        return (
            sa.true()
            if self.expected is None
            else self.comp(attr, self.expected)
        )


@dataclass(frozen=True)
class _JoinBind:
    items: typing.Sequence[BindClause]
    operator: typing.Callable[..., interface.Comparison]

    def bind(self, entity: Mapper) -> interface.Comparison:
        return self.operator(*(item.bind(entity) for item in self.items))


def and_(*bind: BindClause) -> _JoinBind:
    return _JoinBind(bind, sa.and_)


def or_(*bind: BindClause) -> _JoinBind:
    return _JoinBind(bind, sa.or_)
