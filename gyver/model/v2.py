from typing import Any

from lazyfields import lazy
from pydantic import __version__

from gyver import utils

pydantic_vinfo = tuple(int(i) for i in __version__.split(".") if i.isdigit())

if pydantic_vinfo < (2, 0, 0):
    raise ImportError("Unable to use .v2, install pydantic>=2.0.0", __version__)

from pydantic import (  # noqa: E402
    BaseModel,
    ConfigDict,
)


class Model(BaseModel):  # type: ignore
    """
    Model is a BaseModel overload with opinions on mutability and alias generation.

    Configurations:
        - frozen: Model instances are frozen by default.
        - from_attributes: Enables from_attributes mode for this model.
        - alias_generator: Uses utils.to_camel for alias generation.
        - populate_by_name: Allows population of fields by field name.
        - ignore_types: Keeps attributes of type lazy untouched during population.
    """

    model_config = ConfigDict(
        frozen=True,
        populate_by_name=True,
        ignored_types=(lazy,),
        from_attributes=True,
        alias_generator=utils.to_camel,
    )

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

    model_config = ConfigDict(frozen=False)
