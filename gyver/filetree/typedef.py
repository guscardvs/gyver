import sys
from abc import ABC, abstractmethod
from io import SEEK_SET, BytesIO
from typing import Generic

import cchardet
from typing_extensions import Self, TypeVar, override

from gyver.attrs import asdict, call_init, define

T = TypeVar("T")
BoundType = TypeVar("BoundType", str, bytes)


@define
class VirtualPath(Generic[T]):
    name: str
    contents: T


class BaseFile(VirtualPath[BytesIO], Generic[BoundType], ABC):
    def __init__(self, name: str):
        super().__init__(name, BytesIO())

    def get_encoding(self) -> str:
        val = cchardet.detect(self.file_contents())
        self.seek(SEEK_SET)
        return val["encoding"] or sys.getdefaultencoding()

    @abstractmethod
    def read(self, size: int = -1) -> BoundType: ...

    @abstractmethod
    def readline(self, size: int = -1) -> BoundType: ...

    @abstractmethod
    def readlines(self, hint: int = -1) -> list[BoundType]: ...

    @abstractmethod
    def write(self, content: BoundType) -> int: ...

    @abstractmethod
    def writelines(self, lines: list[BoundType]): ...

    def seek(self, offset: int, whence: int = SEEK_SET) -> int:
        return self.contents.seek(offset, whence)

    def tell(self) -> int:
        return self.contents.tell()

    def flush(self):
        self.contents.flush()

    def close(self):
        self.contents.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_):
        self.close()

    def file_contents(self):
        return self.contents.getvalue()

    def __parse_dict__(self, by_alias: bool):
        return {"name": self.name, "contents": self.contents}


class File(BaseFile[bytes]):
    @override
    def read(self, size: int = -1) -> bytes:
        return self.contents.read(size)

    @override
    def readline(self, size: int = -1) -> bytes:
        return self.contents.readline(size)

    @override
    def readlines(self, hint: int = -1) -> list[bytes]:
        return self.contents.readlines(hint)

    @override
    def write(self, content: bytes) -> int:
        return self.contents.write(content)

    @override
    def writelines(self, lines: list[bytes]):
        self.contents.writelines(lines)


@define
class TextFile(BaseFile[str]):
    encoding: str

    def __init__(self, name: str, encoding: str = "utf-8"):
        call_init(self, name, BytesIO(), encoding)

    @override
    def read(self, size: int = -1) -> str:
        return self.contents.read(size).decode(self.encoding)

    @override
    def readline(self, size: int = -1) -> str:
        return self.contents.readline(size).decode(self.encoding)

    @override
    def readlines(self, hint: int = -1) -> list[str]:
        return [line.decode(self.encoding) for line in self.contents.readlines(hint)]

    @override
    def write(self, content: str) -> int:
        return self.contents.write(content.encode(self.encoding))

    @override
    def writelines(self, lines: list[str]):
        encoded_lines = [line.encode(self.encoding) for line in lines]
        self.contents.writelines(encoded_lines)


class Folder(VirtualPath[dict[str, VirtualPath]]):
    def __init__(self, name: str):
        super().__init__(name, {})

    def __parse_dict__(self, by_alias: bool):
        return {
            "name": self.name,
            "contents": {
                key: asdict(value, by_alias) for key, value in self.contents.items()
            },
        }
