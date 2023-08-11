from typing import Any

from pydantic import BaseModel

from gyver import utils
from gyver.utils.lazy import lazy


class Model(BaseModel):
    """Model is a BaseModel overload with some opinions on
    json parsing mutability and alias generation."""

    class Config:
        json_loads = utils.json.loads
        json_dumps = utils.json.dumps
        frozen = True
        orm_mode = True
        alias_generator = utils.to_camel
        allow_population_by_field_name = True
        keep_untouched = (lazy,)

    # Overloading to allow lazyfields to work correctly
    def __setattr__(self, name: str, value: Any):
        if isinstance(
            getattr(type(self), name, None),
            lazy,
        ):
            object.__setattr__(self, name, value)
        else:
            return super().__setattr__(name, value)


class MutableModel(Model):
    class Config:
        frozen = False
