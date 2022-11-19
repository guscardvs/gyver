import contextlib
from inspect import isclass

from typing_extensions import TypeGuard

from gyver.database.entity import AbstractEntity

from .exc import FieldNotFound
from .interface import FieldType
from .interface import Mapper


def retrieve_attr(entity: Mapper, field: str) -> FieldType:
    is_entity = _is_entity(entity)
    if field == "id" and is_entity:
        field = "id_"
    try:
        with contextlib.suppress(AttributeError):
            return getattr(entity, field)
        return getattr(entity.c, field)  # type: ignore
    except AttributeError:
        name = entity.__name__ if is_entity else "query"
        raise FieldNotFound(name, field) from None


def _is_entity(entity: Mapper) -> TypeGuard[type[AbstractEntity]]:
    return isclass(entity) and issubclass(entity, AbstractEntity)
