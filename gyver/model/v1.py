from typing import Any

from lazyfields import lazy

from gyver import utils

try:
    from pydantic.v1 import BaseModel
except ImportError:
    from pydantic import BaseModel


class Model(BaseModel):  # type: ignore
    """
    Model is a BaseModel overload with opinions on JSON parsing mutability and alias generation.

    Configurations:
        - json_loads: Uses utils.json.loads for JSON loading.
        - json_dumps: Uses utils.json.dumps for JSON dumping.
        - frozen: Model instances are frozen by default.
        - orm_mode: Enables ORM mode for this model.
        - alias_generator: Uses utils.to_camel for alias generation.
        - allow_population_by_field_name: Allows population of fields by field name.
        - keep_untouched: Keeps attributes of type lazy untouched during population.
    """

    class Config:
        json_loads = utils.json.loads
        json_dumps = utils.json.dumps
        frozen = True
        orm_mode = True
        alias_generator = utils.to_camel
        allow_population_by_field_name = True
        keep_untouched = (lazy,)

    def __setattr__(self, name: str, value: Any):
        """
        Overloads the __setattr__ method to allow lazy fields to work correctly.

        Args:
            name (str): The name of the attribute.
            value (Any): The value to set for the attribute.
        """
        if isinstance(getattr(type(self), name, None), lazy):
            object.__setattr__(self, name, value)
        else:
            return super().__setattr__(name, value)


class MutableModel(Model):
    """
    A mutable version of the Model class that allows unfreezing of instances.

    Configurations:
        - frozen: Model instances are not frozen, allowing mutability.
    """

    class Config:
        frozen = False
