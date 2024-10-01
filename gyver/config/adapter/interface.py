from typing import TYPE_CHECKING
from typing import Any
from collections.abc import Generator
from typing import Protocol
from collections.abc import Sequence
from typing import TypeVar

from config import MISSING

if TYPE_CHECKING:
    from dataclasses import Field

    from attrs import Attribute
    from gyver.attrs.field import Field as GField

    from .pydantic import FieldWrapper

T_co = TypeVar("T_co", "FieldWrapper", "Attribute", "Field", "GField", covariant=True)


class FieldResolverStrategy(Protocol[T_co]):
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

    def __init__(self, field: T_co) -> None:
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

    def default(self) -> Any | type[MISSING]:
        """
        Get the default value of the field.

        :return: The default value of the field,
        or the special value `MISSING` (from the `config` module)
        if no default is defined.
        """
        ...

    @staticmethod
    def iterfield(config_class: type) -> Generator[T_co, Any, Any]: ...
