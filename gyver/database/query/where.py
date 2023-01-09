import typing

import sqlalchemy as sa

from gyver.database.typedef import ClauseType

from . import _helpers
from . import comp as cp
from . import interface

T = typing.TypeVar("T")


class Where(interface.BindClause, typing.Generic[T]):
    def __init__(
        self,
        field: str,
        expected: typing.Optional[T] = None,
        comp: interface.Comparator[T] = cp.equals,
    ) -> None:
        self.field = field
        self.expected = expected
        self.comp = comp

    type_ = ClauseType.BIND

    def bind(self, mapper: interface.Mapper) -> interface.Comparison:
        if self.comp is cp.always_true:
            return AlwaysTrue().bind(mapper)
        attr = _helpers.retrieve_attr(mapper, self.field)
        return (
            sa.true()
            if self.expected is None
            else self.comp(attr, self.expected)
        )


class _JoinBind(interface.BindClause):
    def __init__(
        self,
        items: typing.Sequence[interface.BindClause],
        operator: typing.Callable[..., interface.Comparison],
    ) -> None:
        self.items = items
        self.operator = operator

    type_ = ClauseType.BIND

    def bind(self, mapper: interface.Mapper) -> interface.Comparison:
        return self.operator(*(item.bind(mapper) for item in self.items))


def and_(*bind: interface.BindClause) -> _JoinBind:
    return _JoinBind(bind, sa.and_)


def or_(*bind: interface.BindClause) -> _JoinBind:
    return _JoinBind(bind, sa.or_)


_placeholder_column = sa.Column("placeholder")


class AlwaysTrue(interface.BindClause):
    type_ = ClauseType.BIND

    def bind(self, mapper: interface.Mapper) -> interface.Comparison:
        return cp.always_true(_placeholder_column, mapper)
