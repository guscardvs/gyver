import contextlib
import typing

import sqlalchemy as sa
from gyver.attrs import call_init
from gyver.attrs import define

from gyver.database.typedef import ClauseType

from . import _helpers
from . import comp as cp
from . import interface

T = typing.TypeVar("T")

CACHE_MAXLEN = 250


class _BindCache:
    def __init__(self) -> None:
        self._cached: dict[typing.Hashable, interface.Comparison] = {}
        self.maxlen = CACHE_MAXLEN

    def get(self, key: typing.Hashable) -> typing.Optional[interface.Comparison]:
        try:
            return self._cached.get(key)
        except TypeError:
            return None

    def set(
        self, key: typing.Hashable, value: interface.Comparison
    ) -> interface.Comparison:
        if len(self._cached) >= CACHE_MAXLEN:
            self._cached.pop(tuple(self._cached)[0])
        with contextlib.suppress(TypeError):
            self._cached[key] = value
        return value

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.clear()

    def clear(self):
        self._cached.clear()


_cache = _BindCache()


@define
class Resolver(typing.Generic[T]):
    val: typing.Any

    def resolve(self, mapper: interface.Mapper):
        del mapper
        val = self.val
        if isinstance(val, list):
            return tuple(val)
        elif isinstance(val, set):
            return frozenset(val)
        return val

    def __bool__(self):
        return self.val is not None


class FieldResolver(Resolver[str]):
    def resolve(self, mapper: interface.Mapper):
        return _helpers.retrieve_attr(mapper, self.val)


@define(frozen=False)
class Where(interface.BindClause, typing.Generic[T]):
    field: str
    expected: Resolver[T]
    comp: interface.Comparator[T] = cp.equals

    def __init__(
        self,
        field: str,
        expected: typing.Optional[T] = None,
        comp: interface.Comparator[T] = cp.equals,
        resolver_class: type[Resolver[T]] = Resolver,
    ) -> None:
        call_init(
            self,
            field,
            resolver_class(expected),
            comp,
        )

    type_ = ClauseType.BIND

    def bind(self, mapper: interface.Mapper) -> interface.Comparison:
        if self.comp is cp.always_true:
            return AlwaysTrue().bind(mapper)
        resolved = self.expected.resolve(mapper)
        if not isinstance(mapper, typing.Hashable):
            return self._get_comparison(
                _helpers.retrieve_attr(mapper, self.field),
                resolved,
            )
        if (value := _cache.get((mapper, self.field, resolved, self.comp))) is not None:
            return value
        attr = _helpers.retrieve_attr(mapper, self.field)

        return _cache.set(
            (mapper, self.field, resolved, self.comp),
            self._get_comparison(attr, resolved),
        )

    def _get_comparison(self, attr: interface.FieldType, resolved: typing.Any):
        return self.comp(attr, resolved) if self.expected else sa.true()


class _JoinBind(interface.BindClause):
    def __init__(
        self,
        items: typing.Sequence[interface.BindClause],
        operator: typing.Callable[..., interface.Comparison],
    ) -> None:
        self.items = items
        self.operator = operator

    type_ = ClauseType.BIND

    def __bool__(self):
        return bool(self.items)

    def bind(self, mapper: interface.Mapper) -> interface.Comparison:
        return (
            self.operator(*(item.bind(mapper) for item in self.items))
            if self
            else sa.true()
        )


def and_(*bind: interface.BindClause) -> _JoinBind:
    return _JoinBind(bind, sa.and_)


def or_(*bind: interface.BindClause) -> _JoinBind:
    return _JoinBind(bind, sa.or_)


_placeholder_column = sa.Column("placeholder")


class AlwaysTrue(interface.BindClause):
    type_ = ClauseType.BIND

    def bind(self, mapper: interface.Mapper) -> interface.Comparison:
        return cp.always_true(_placeholder_column, mapper)


class RawQuery(interface.BindClause):
    type_ = ClauseType.BIND

    def __init__(self, cmp: interface.Comparison) -> None:
        self._cmp = cmp

    def bind(self, mapper: interface.Mapper) -> interface.Comparison:
        del mapper
        return self._cmp


class ApplyWhere(interface.ApplyClause):
    type_ = ClauseType.APPLY

    def __init__(self, mapper: interface.Mapper, *where: interface.BindClause) -> None:
        self.where = and_(*where).bind(mapper)

    def apply(self, query: interface.ExecutableT) -> interface.ExecutableT:
        return query.where(self.where)
