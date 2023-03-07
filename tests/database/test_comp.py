from datetime import datetime

import sqlalchemy as sa

from gyver.database import query

from .mocks import Another
from .mocks import Person
from .mocks import PersonAddress
from .mocks import build_query


def test_comparison_matches_expected():  # sourcery skip: none-compare

    assert query.comp.always_true(Person.name, object()) == sa.true()
    assert build_query(query.comp.equals(Person.name, "test")) == build_query(
        Person.name == "test"
    )
    assert build_query(query.comp.not_equals(Person.name, "test")) == build_query(
        Person.name != "test"
    )
    assert build_query(query.comp.greater(Person.age, 46)) == build_query(
        Person.age > 46
    )
    assert build_query(query.comp.greater_equals(Person.age, 46)) == build_query(
        Person.age >= 46
    )
    assert build_query(query.comp.lesser(Person.age, 46)) == build_query(
        Person.age < 46
    )
    assert build_query(query.comp.lesser_equals(Person.age, 46)) == build_query(
        Person.age <= 46
    )
    assert build_query(query.comp.between(Person.age, (45, 52))) == build_query(
        Person.age.between(45, 52)
    )
    assert build_query(query.comp.range(Person.age, (45, 52))) == build_query(
        sa.and_(Person.age >= 45, Person.age < 52)
    )
    assert build_query(query.comp.like(Person.name, "test")) == build_query(
        Person.name.like("%test%")
    )
    assert build_query(query.comp.rlike(Person.name, "test")) == build_query(
        Person.name.like("test%")
    )
    assert build_query(query.comp.llike(Person.name, "test")) == build_query(
        Person.name.like("%test")
    )
    assert build_query(
        query.comp.insensitive_like()(Person.name, "test")
    ) == build_query(Person.name.ilike("%test%"))
    assert build_query(
        query.comp.insensitive_like("llike")(Person.name, "test")
    ) == build_query(Person.name.ilike("test%"))
    assert build_query(
        query.comp.insensitive_like("rlike")(Person.name, "test")
    ) == build_query(Person.name.ilike("%test"))
    assert build_query(query.comp.isnull(Person.name, True)) == build_query(
        Person.name.is_(None)
    )
    assert build_query(query.comp.isnull(Person.name, False)) == build_query(
        Person.name.is_not(None)
    )
    now = datetime.now()
    assert build_query(
        query.as_date(query.comp.equals)(Person.last_login, now.date())
    ) == build_query(sa.func.date(Person.last_login) == now.date())
    assert build_query(
        query.as_time(query.comp.greater)(Person.last_login, now.time())
        == build_query(sa.func.time(Person.last_login) > now.time())
    )


def test_field_resolver_resolves_correctly():
    assert build_query(
        query.Where(
            "another.id", "another_id", resolver_class=query.FieldResolver
        ).bind(PersonAddress)
    ) == build_query(Another.id_ == PersonAddress.another_id)
