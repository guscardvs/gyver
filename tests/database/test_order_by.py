import pytest
import sqlalchemy as sa

from gyver.database import query

from .mocks import Another


def test_should_apply_returns_expected_value():
    assert not query.OrderBy.none()._should_apply
    assert query.OrderBy.asc("name")._should_apply
    assert query.OrderBy.desc("name")._should_apply


def test_find_column_returns_expected_col_from_query():
    q = sa.select(Another)

    assert query.OrderBy.asc("name")._find_column(q) is next(
        iter(Another.name.base_columns)
    )
    assert query.OrderBy.desc("id")._find_column(q) is next(
        iter(Another.id_.base_columns)
    )


def test_find_column_raises_value_error_if_col_not_in_query():
    with pytest.raises(ValueError):
        query.OrderBy.asc("name")._find_column(sa.select(Another.id_))


def test_apply_order_applies_correct_order():
    assert str(query.OrderBy.desc("id")._apply_order(Another.id_)) == str(
        Another.id_.desc()
    )
    assert str(query.OrderBy.asc("id")._apply_order(Another.id_)) == str(
        Another.id_.asc()
    )


def test_apply_returns_ordered_select():
    q = sa.select(Another)
    assert str(query.OrderBy.asc("name").apply(q)) == str(
        q.order_by(Another.name.asc())
    )
