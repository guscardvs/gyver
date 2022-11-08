import typing

import orjson

loads = orjson.loads


def dumps(val: typing.Any, *, default: typing.Any = None) -> str:
    return orjson.dumps(val, default=default).decode()
