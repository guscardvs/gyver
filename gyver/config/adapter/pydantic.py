from typing import Any
from typing import Generator
from typing import Sequence
from typing import Union

from config import MISSING
from gyver.attrs import define
from pydantic import BaseModel
from pydantic.fields import ModelField

from gyver.config.adapter.interface import FieldResolverStrategy


@define
class PydanticResolverStrategy(FieldResolverStrategy[ModelField]):
    field: ModelField

    def cast(self) -> type:
        return self.field.outer_type_

    def names(self) -> Sequence[str]:
        return (self.field.name, self.field.alias)

    def init_name(self) -> str:
        return self.field.name

    def default(self) -> Union[Any, type[MISSING]]:
        if self.field.default not in (None, Ellipsis):
            return self.field.default
        return (
            MISSING
            if self.field.default_factory is None
            else self.field.default_factory
        )

    @staticmethod
    def iterfield(
        config_class: type[BaseModel],
    ) -> Generator[ModelField, Any, Any]:
        yield from config_class.__fields__.values()
