from enum import Enum
from typing import NamedTuple

from typing_extensions import Self


class EnvTuple(NamedTuple):
    val: str
    weight: int


class Env(EnvTuple, Enum):
    LOCAL = "local", 1
    TEST = "test", 2
    DEV = "dev", 3
    PRD = "prd", 4

    @property
    def value(self) -> EnvTuple:
        return super().value

    @property
    def val(self):
        return self.value.val

    @property
    def weight(self):
        return self.value.weight

    @classmethod
    def new(cls, val: str) -> Self:
        return next(value for value in cls if value.val == val)
