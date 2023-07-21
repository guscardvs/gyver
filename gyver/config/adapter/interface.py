from typing import TYPE_CHECKING
from typing import Any
from typing import Generator
from typing import Protocol
from typing import Sequence
from typing import TypeVar
from typing import Union

from gyver.config.config import MISSING

if TYPE_CHECKING:
    from dataclasses import Field

    from attrs import Attribute
    from gyver.attrs.field import Field as GField
    from pydantic.fields import ModelField

T = TypeVar("T", "ModelField", "Attribute", "Field", "GField")


class FieldResolverStrategy(Protocol[T]):
    """
    A protocol for resolving the properties of a field, regardless of
    its implementation.

    The `FieldResolver` protocol is defined to be generic over `T`,
    which is restricted to be one of three possible types:
    - `ModelField` from the `pydantic` library
    - `Attribute` from the `attrs` library
    - `Field` from the `dataclasses` library

    These types indicate the different ways that a field can be defined in Python.
    """

    def __init__(self, field: T) -> None:
        """
        Initialize a new `FieldResolver` instance.

        :param field: An instance of one of the three types `T` can be.
        """
        ...

    def names(self) -> Sequence[str]:
        """
        Get the names by which the field can be accessed.

        :return: A sequence of strings, representing the names.
        """
        ...

    def init_name(self) -> str:
        """
        Get the name by which the field is expected in init.

        :return: A sequence of strings, representing the names.
        """
        ...

    def cast(self) -> type:
        """
        Get the type of the field.

        :return: The type of the field.
        """
        ...

    def default(self) -> Union[Any, type[MISSING]]:
        """
        Get the default value of the field.

        :return: The default value of the field,
        or the special value `MISSING` (from the `gyver.config.config` module)
        if no default is defined.
        """
        ...

    @staticmethod
    def iterfield(config_class: type) -> Generator[T, Any, Any]:
        ...
