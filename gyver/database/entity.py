from typing import Any
from typing import TypeVar
from typing import final

import sqlalchemy as sa
from sqlalchemy.orm import as_declarative
from sqlalchemy.orm import declared_attr

from .metadata import metadata

T = TypeVar("T")


def _wrap(cls: type[T]) -> type[T]:
    return as_declarative(metadata=metadata)(cls)


@_wrap
class AbstractEntity:
    """Default Entity Representation without default primary key"""

    @final
    @declared_attr
    def __tablename__(self):
        return self.classname()

    @classmethod
    def classname(cls):
        """Override this method to change tablename default"""
        return cls.__name__.lower()


class Entity(AbstractEntity):
    """Entity Representation with default id autoincrement as primary key"""

    __abstract__ = True

    @final
    @declared_attr
    def id_(self):
        return sa.Column("id", sa.Integer, primary_key=True)

    @property
    def pk(self):
        return self.id_


def make_table(name: str, *args: Any, **kwargs: Any) -> sa.Table:
    return sa.Table(name, metadata, *args, **kwargs)
