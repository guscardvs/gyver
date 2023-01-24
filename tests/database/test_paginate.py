import sqlalchemy as sa

from gyver.database import query

from .mocks import Person
from .mocks import build_query


def test_limit_offset_paginate_return_valid_paginate_query():
    built_query = query.select(Person).apply(query.LimitOffsetPaginate(10, 5)).get()
    sa_query = sa.select(Person).limit(10).offset(5)

    assert build_query(built_query) == build_query(sa_query)


def test_id_paginate_return_valid_paginate_query():
    built_query = query.select(Person).apply(query.IdPaginate(10, 5)).get()
    sa_query = sa.select(Person).where(Person.id_ > 5).limit(10)

    assert build_query(built_query) == build_query(sa_query)


def test_null_paginate_returns_same_query_as_received():
    query_obj = query.select(Person)
    initial = query_obj.get()
    null_passed = query_obj.apply(query.Paginate.none()).get()

    assert build_query(initial) == build_query(null_passed)
