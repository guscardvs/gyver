from dataclasses import MISSING as dc_MISSING
from dataclasses import Field
from dataclasses import fields
from typing import Any
from collections.abc import Generator
from collections.abc import Sequence

from config import MISSING
from gyver.attrs import define

from gyver.config.adapter.interface import FieldResolverStrategy


@define
class DataclassResolverStrategy(FieldResolverStrategy[Field]):
    field: Field

    def cast(self) -> type:
        return self.field.type

    def names(self) -> Sequence[str]:
        return (self.field.name,)

    def init_name(self) -> str:
        return self.field.name

    def default(self) -> Any | type[MISSING]:
        if self.field.default not in (None, Ellipsis, dc_MISSING):
            return self.field.default
        return (
            MISSING
            if self.field.default_factory in (None, dc_MISSING)
            else self.field.default_factory
        )

    @staticmethod
    def iterfield(config_class: type) -> Generator[Field, Any, Any]:
        yield from fields(config_class)
