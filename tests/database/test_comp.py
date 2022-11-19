from datetime import datetime

import sqlalchemy as sa

from gyver.database import query

from .mocks import Person


def test_comparison_matches_expected():  # sourcery skip: none-compare

    assert query.comp.always_true(Person.name, object()) == sa.true()
    assert str(query.comp.equals(Person.name, "test")) == str(
        Person.name == "test"
    )
    assert str(query.comp.not_equals(Person.name, "test")) == str(
        Person.name != "test"
    )
    assert str(query.comp.greater(Person.age, 46)) == str(Person.age > 46)
    assert str(query.comp.greater_equals(Person.age, 46)) == str(
        Person.age >= 46
    )
    assert str(query.comp.lesser(Person.age, 46)) == str(Person.age < 46)
    assert str(query.comp.lesser_equals(Person.age, 46)) == str(
        Person.age <= 46
    )
    assert str(query.comp.between(Person.age, (45, 52))) == str(
        Person.age.between(45, 52)
    )
    assert str(query.comp.range(Person.age, (45, 52))) == str(
        sa.and_(Person.age >= 45, Person.age < 52)
    )
    assert str(query.comp.like(Person.name, "test")) == str(
        Person.name.like("%test%")
    )
    assert str(query.comp.rlike(Person.name, "test")) == str(
        Person.name.like("test%")
    )
    assert str(query.comp.llike(Person.name, "test")) == str(
        Person.name.like("%test")
    )
    assert str(query.comp.insensitive_like()(Person.name, "test")) == str(
        Person.name.ilike("%test%")
    )
    assert str(
        query.comp.insensitive_like("llike")(Person.name, "test")
    ) == str(Person.name.ilike("test%"))
    assert str(
        query.comp.insensitive_like("rlike")(Person.name, "test")
    ) == str(Person.name.ilike("%test"))
    assert str(query.comp.isnull(Person.name, True)) == str(
        Person.name.is_(None)
    )
    assert str(query.comp.isnull(Person.name, False)) == str(
        Person.name.is_not(None)
    )
    now = datetime.now()
    assert str(
        query.as_date(query.comp.equals)(Person.last_login, now.date())
    ) == str(sa.func.date(Person.last_login) == now.date())
    assert str(
        query.as_time(query.comp.greater)(Person.last_login, now.time())
        == str(sa.func.time(Person.last_login) > now.time())
    )
