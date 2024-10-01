from typing import Any
from collections.abc import Generator
from collections.abc import Sequence

from config import MISSING
from gyver.attrs import define
from gyver.attrs import fields
from gyver.attrs.field import Field
from gyver.attrs.utils.typedef import MISSING as NOTHING

from gyver.config.adapter.interface import FieldResolverStrategy


@define
class GyverAttrsResolverStrategy(FieldResolverStrategy[Field]):
    field: Field

    def cast(self) -> type:
        return self.field.declared_type

    def names(self) -> Sequence[str]:
        return self.field.name, self.field.alias

    def init_name(self) -> str:
        return self.field.alias or self.field.name

    def default(self) -> Any | type[MISSING]:
        default = self.field.default
        if default is NOTHING:
            return MISSING
        return default() if self.field.has_default_factory else default

    @staticmethod
    def iterfield(config_class: type) -> Generator[Field, Any, Any]:
        yield from fields(config_class).values()
