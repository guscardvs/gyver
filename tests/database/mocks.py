import sqlalchemy as sa

from gyver.database import Entity
from gyver.database.query.interface import ExecutableType


class Person(Entity):
    name = sa.Column(sa.Text)
    age = sa.Column(sa.Integer)
    birth_date = sa.Column(sa.Date)
    last_login = sa.Column(sa.TIMESTAMP)


class Another(Entity):
    name = sa.Column(sa.Text)


def build_query(query: ExecutableType):
    return str(query.compile(compile_kwargs={"literal_binds": True}))
