import typing

import orjson


loads: typing.Callable[
    [typing.Union[str, bytes, bytearray, memoryview]], typing.Any
] = orjson.loads
"""
Deserialize a JSON string to a Python object.

Args:
    s (bytes, str, bytearray, memoryview): The JSON string to be deserialized.

Returns:
    typing.Any: The deserialized Python object.
"""


def dumps(val: typing.Any, *, default: typing.Any = None) -> str:
    """
    Serialize a Python object to a JSON-formatted string.

    Args:
        val (typing.Any): The Python object to be serialized.
        default (typing.Any, optional): A default value to be used if an object is not serializable.
            Defaults to None.

    Returns:
        str: The JSON-formatted string representing the serialized object.
    """
    return orjson.dumps(val, default=default).decode()


def load(fdes: typing.TextIO) -> str:
    """
    Deserialize a JSON-formatted string from a text file object.

    Args:
        fdes (typing.TextIO): The text file object to read the JSON-formatted string from.

    Returns:
        typing.Any: The deserialized Python object.
    """
    return loads(fdes.read())


def dump(val: typing.Any, fp: typing.TextIO, *, default: typing.Any = None):
    """
    Serialize a Python object and write the JSON-formatted string to a text file object.

    Args:
        val (typing.Any): The Python object to be serialized.
        fp (typing.TextIO): The text file object to write the JSON-formatted string to.
        default (typing.Any, optional): A default value to be used if an object is not serializable.
            Defaults to None.
    """
    return fp.write(dumps(val, default=default))
