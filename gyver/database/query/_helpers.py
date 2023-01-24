import contextlib
from inspect import isclass
from typing import cast

from sqlalchemy.sql import ColumnElement
from typing_extensions import TypeGuard

from gyver.database.entity import AbstractEntity

from .exc import FieldNotFound
from .interface import FieldType
from .interface import Mapper


def retrieve_attr(entity: Mapper, field: str) -> FieldType:
    is_entity = _is_entity(entity)
    if field == "id" and is_entity:
        field = "id_"
    if "." in field:
        if is_entity:
            return _retrieve_related_field(entity, field)
        raise FieldNotFound("query", field)
    try:
        with contextlib.suppress(AttributeError):
            return getattr(entity, field)
        return getattr(entity.c, field)  # type: ignore
    except AttributeError:
        name = entity.__name__ if is_entity else "query"
        raise FieldNotFound(name, field) from None


def _is_entity(entity: Mapper) -> TypeGuard[type[AbstractEntity]]:
    return isclass(entity) and issubclass(entity, AbstractEntity)


def _retrieve_related_field(entity: type[AbstractEntity], field: str) -> FieldType:
    *fields, target_field = field.split(".")
    current_mapper = entity
    for f in fields:
        if f == "id":
            f = "id_"
        try:
            attr = cast(ColumnElement, getattr(current_mapper, f))
        except AttributeError:
            raise FieldNotFound(entity.__name__, f) from None
        else:
            current_mapper = attr.entity.class_
    if target_field == "id":
        target_field = "id_"
    try:
        return getattr(current_mapper, target_field)
    except AttributeError:
        raise FieldNotFound(entity.__name__, field) from None
