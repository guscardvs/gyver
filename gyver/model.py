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


class MutableModel(BaseModel):
    class Config:
        frozen = False
