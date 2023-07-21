from typing import Any
from typing import Callable
from typing import Protocol

import sqlalchemy as sa

from gyver.database import Entity
from gyver.database.entity import make_table
from gyver.database.utils import create_relation_table
from gyver.database.utils import make_relation


class Person(Entity):
    name = sa.Column(sa.Text)
    age = sa.Column(sa.Integer)
    birth_date = sa.Column(sa.Date)
    last_login = sa.Column(sa.TIMESTAMP)


class Another(Entity):
    name = sa.Column(sa.Text)


class PersonAddress(Entity):
    another_id = sa.Column(sa.Integer, sa.ForeignKey("another.id"))

    another = make_relation(Another)
    related_person = make_relation(
        lambda: RelatedPerson,
        relation_name="RelatedPerson",
        back_populates="address",
    )


related_person_person_address = create_relation_table(
    "relatedperson_personaddress", "personaddress", "relatedperson"
)


class RelatedPerson(Entity):
    address_id = sa.Column(sa.Integer, sa.ForeignKey("personaddress.id"))

    address = make_relation(PersonAddress, secondary=related_person_person_address)


mock_table = make_table("mock_table", sa.Column("id", sa.Integer, primary_key=True))


class HasCompile(Protocol):
    compile: Callable[..., Any]


def build_query(query: HasCompile):
    return str(query.compile(compile_kwargs={"literal_binds": True}))
