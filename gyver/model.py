from typing import Any

from pydantic import BaseModel

from gyver import utils


class Model(BaseModel):
    class Config:
        json_loads = utils.json.loads
        json_dumps = utils.json.dumps
        frozen = True
        orm_mode = True
        alias_generator = utils.to_camel
        allow_population_by_field_name = True
        keep_untouched = (utils.lazyfield,)

    def __setattr__(self, name: str, value: Any):
        if isinstance(getattr(type(self), name, None), utils.lazyfield):
            object.__setattr__(self, name, value)
            return
        return super().__setattr__(name, value)


class MutableModel(BaseModel):
    class Config:
        frozen = False
