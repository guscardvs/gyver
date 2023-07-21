from typing import Any
from typing import Generator
from typing import Sequence
from typing import Union

from attr._make import Factory
from attrs import NOTHING
from attrs import Attribute
from attrs import fields
from gyver.attrs import define

from gyver.config.adapter.interface import FieldResolverStrategy
from gyver.config.config import MISSING
from gyver.exc import InvalidCast
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

    def default(self) -> Union[Any, type[MISSING]]:
        default = self.field.default
        if default is None or default in (Ellipsis, NOTHING):
            return MISSING
        return default.factory() if isinstance(default, Factory) else default

    @staticmethod
    def iterfield(config_class: type) -> Generator[Attribute, Any, Any]:
        yield from fields(config_class)
