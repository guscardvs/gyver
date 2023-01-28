import abc
from typing import Union


class Encodable(abc.ABC):
    @abc.abstractmethod
    def encode(self) -> str:
        raise NotImplementedError

    def __eq__(self, other: Union["Encodable", str]) -> bool:
        if isinstance(other, str):
            return self.encode() == other
        return self.encode() == other.encode() or super().__eq__(other)

    def __str__(self) -> str:
        return self.encode()
