import typing

import orjson

loads = orjson.loads


def dumps(val: typing.Any, *, default: typing.Any = None) -> str:
    return orjson.dumps(val, default=default).decode()


def load(fdes: typing.TextIO) -> str:
    return loads(fdes.read())


def dump(val: typing.Any, fp: typing.TextIO, *, default: typing.Any = None):
    return fp.write(dumps(val, default=default))
