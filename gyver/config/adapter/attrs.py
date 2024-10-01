from typing import Any
from collections.abc import Generator, Sequence

from attr._make import Factory
from attrs import NOTHING, Attribute, fields
from config import MISSING
from config.exceptions import InvalidCast

from gyver.attrs import define
from gyver.config.adapter.interface import FieldResolverStrategy
from gyver.utils import panic


@define
class AttrsResolverStrategy(FieldResolverStrategy[Attribute]):
    field: Attribute

    def cast(self) -> type:
        if field_type := self.field.type:
            return field_type
        raise panic(InvalidCast, f"Field {self.field.name} has no valid type")

    def names(self) -> Sequence[str]:
        return tuple(
            item for item in (self.field.name, self.field.alias) if item is not None
        )

    def init_name(self) -> str:
        return self.field.alias or self.field.name

    def default(self) -> Any | type[MISSING]:
        default = self.field.default
        if default is None or default in (Ellipsis, NOTHING):
            return MISSING
        return default.factory() if isinstance(default, Factory) else default

    @staticmethod
    def iterfield(config_class: type) -> Generator[Attribute, Any, Any]:
        yield from fields(config_class)
