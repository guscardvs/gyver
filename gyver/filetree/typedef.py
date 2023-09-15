import sys
from io import SEEK_SET
from io import BytesIO
from typing import Generic
from typing import TypeVar

import cchardet
from gyver.attrs import define
from typing_extensions import Self

T = TypeVar("T")


@define
class VirtualPath(Generic[T]):
    name: str
    contents: T


class File(VirtualPath[BytesIO]):
    def get_encoding(self):
        val = cchardet.detect(self.getvalue())
        self.seek(SEEK_SET)
        return val["encoding"] or sys.getdefaultencoding()

    @classmethod
    def new(cls, name: str) -> Self:
        return cls(name, BytesIO())

    def read(self, size: int = -1) -> bytes:
        return self.contents.read(size)

    def readline(self, size: int = -1) -> bytes:
        return self.contents.readline(size)

    def readlines(self, hint: int = -1) -> list[bytes]:
        return self.contents.readlines(hint)

    def write(self, content: bytes) -> int:
        return self.contents.write(content)

    def writelines(self, lines: list[bytes]):
        self.contents.writelines(lines)

    def seek(self, offset: int, whence: int = SEEK_SET) -> int:
        return self.contents.seek(offset, whence)

    def tell(self) -> int:
        return self.contents.tell()

    def flush(self):
        self.contents.flush()

    def close(self):
        self.contents.close()

    def __enter__(self) -> "File":
        return self

    def __exit__(self, *_):
        self.close()

    def getvalue(self):
        return self.contents.getvalue()

    def __parse_dict__(self, by_alias: bool):
        return {"name": self.name, "contents": self.contents}


@define
class TextFile(File):
    encoding: str

    @classmethod
    def new(cls, name: str):
        return cls(name, BytesIO(), sys.getdefaultencoding())

    def read(self, size: int = -1) -> str:
        return self.contents.read(size).decode(self.encoding)

    def readline(self, size: int = -1) -> str:
        return self.contents.readline(size).decode(self.encoding)

    def readlines(self, hint: int = -1) -> list[str]:
        return [line.decode(self.encoding) for line in self.contents.readlines(hint)]

    def write(self, text: str) -> int:
        return self.contents.write(text.encode(self.encoding))

    def writelines(self, lines: list[str]):
        encoded_lines = [line.encode(self.encoding) for line in lines]
        self.contents.writelines(encoded_lines)

    def getvalue(self) -> str:
        return self.contents.getvalue().decode(self.encoding)


class Folder(VirtualPath[dict[str, VirtualPath]]):
    @classmethod
    def new(cls, name: str) -> Self:
        return cls(name, {})

    def __parse_dict__(self, by_alias: bool):
        return {
            "name": self.name,
            "contents": {
                key: value.__parse_dict__(by_alias)
                for key, value in self.contents.items()
            },
        }
