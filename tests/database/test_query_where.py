from unittest.mock import MagicMock
import sqlalchemy as sa
import pytest
from gyver.database.query.where import (
    _BindCache,
    Resolver,
    FieldResolver,
    Where,
    _JoinBind,
    and_,
    or_,
    AlwaysTrue,
    RawQuery,
    _cache,
    CACHE_MAXLEN,
)
from gyver.database.query import comp
from gyver.database import default_metadata
from tests.database.mocks import build_query

mapper = sa.Table(
    "users",
    default_metadata,
    sa.Column("id", sa.Integer),
    sa.Column("name", sa.String),
)


@pytest.fixture(autouse=True)
def reset_cache():
    with _cache:
        yield


def test_get_with_existing_key():
    cache = _BindCache()
    key = "test"
    value = MagicMock()
    cache._cached[key] = value

    assert cache.get(key) == value


def test_get_with_non_existing_key():
    cache = _BindCache()
    key = "test"

    assert cache.get(key) is None


def test_set():
    cache = _BindCache()
    key = "test"
    value = MagicMock()

    assert cache.set(key, value) == value
    assert cache._cached[key] == value


def test_set_with_cache_overflow():
    cache = _BindCache()
    for i in range(CACHE_MAXLEN):
        cache.set(i, MagicMock())

    key = "test"
    value = MagicMock()
    assert cache.set(key, value) is value
    assert key in cache._cached and 0 not in cache._cached


def test_resolve_with_list():
    resolver = Resolver[list[int]]([1, 2, 3])
    resolved = resolver.resolve(mapper)
    assert resolved == (1, 2, 3)
    assert isinstance(resolved, tuple)


def test_resolve_with_set():
    resolver = Resolver[set[int]]({1, 2, 3})
    resolved = resolver.resolve(mapper)
    assert resolved == frozenset({1, 2, 3})
    assert isinstance(resolved, frozenset)


def test_resolve_with_other_type():
    resolver = Resolver[int](5)
    assert resolver.resolve(mapper) == 5


def test_bool_with_none():
    resolver = Resolver[int](None)
    assert not resolver


def test_bool_with_non_none():
    resolver = Resolver[int](5)
    assert bool(resolver)


def test_resolve():
    resolver = FieldResolver("id")
    assert resolver.resolve(mapper) == mapper.c.id


def test_bind_with_always_true_comp():
    mapper = MagicMock()
    where = Where("id", 5, comp.always_true)
    assert where.bind(mapper) == AlwaysTrue().bind(mapper)


def test_bind_with_non_hashable_mapper():
    mapper = MagicMock()
    mapper.id = 5
    mapper.__hash__ = lambda: NotImplemented
    where = Where("id", 5)
    where._get_comparison = MagicMock()
    result = where.bind(mapper)

    assert result == where._get_comparison.return_value
    where._get_comparison.assert_called_once_with(mapper.id, 5)
    assert _cache.get((mapper, "id", 5, comp.equals)) is None


def test_bind_with_hashable_mapper():
    where = Where("id", 5)
    where._get_comparison = MagicMock()
    result = where.bind(mapper)

    assert result == where._get_comparison.return_value
    where._get_comparison.assert_called_once_with(mapper.c.id, 5)
    assert _cache.get((mapper, "id", 5, comp.equals)) is result


def test_where_bind_returns_valid_comparison():
    where = Where("id", 5)
    assert build_query(where.bind(mapper)) == build_query(mapper.c.id == 5)


def test_where_resolves_value_on_bind():
    class MyResolver(Resolver[int]):
        def resolve(self, mapper):
            _ = mapper
            return self.val * 2

    where = Where("id", 5, resolver_class=MyResolver)
    where._get_comparison = MagicMock()
    where.bind(mapper)

    where._get_comparison.assert_called_once_with(mapper.c.id, 10)


def test_where_runs_correctly_other_comp():
    where = Where("id", 5, comp.greater)
    assert build_query(where.bind(mapper)) == build_query(mapper.c.id > 5)


def test_join_bind_runs_equally_without_args():
    assert (
        build_query(and_().bind(mapper))
        == build_query(or_().bind(mapper))
        == build_query(sa.true())
    )


def test_join_bind_returns_expected_value():
    assert build_query(
        and_(
            Where("id", 5, comp.greater), Where("id", 10, comp.lesser_equals)
        ).bind(mapper)
    ) == build_query(sa.and_(mapper.c.id > 5, mapper.c.id <= 10))
    assert build_query(
        or_(
            Where("id", 5, comp.greater), Where("id", 10, comp.lesser_equals)
        ).bind(mapper)
    ) == build_query(sa.or_(mapper.c.id > 5, mapper.c.id <= 10))


def test_raw_query_returns_same_value_received():
    q = mapper.c.id > 5

    assert RawQuery(q).bind(mapper) is q
