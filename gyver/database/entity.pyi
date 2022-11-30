import typing

import sqlalchemy as sa

class AbstractEntity:

    metadata: typing.ClassVar[sa.MetaData]

    def __init__(self, **kwargs: typing.Any) -> None: ...
    @classmethod
    def __tablename__(cls) -> str: ...
    @classmethod
    def classname(cls) -> str: ...

class Entity(AbstractEntity):
    id_: sa.Column[sa.Integer]

    @property
    def pk(self) -> sa.Column[sa.Integer]: ...

def make_table(
    name: str, *args: sa.schema.SchemaItem, **kwargs: typing.Any
) -> sa.Table: ...
