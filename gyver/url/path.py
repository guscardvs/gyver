import re
from typing import Union
from urllib.parse import quote
from urllib.parse import unquote

from gyver.url.encode import Encodable
from gyver.url.utils import is_valid_encoded_path
from gyver.url.utils import utf8

PERCENT_REGEX = r"\%[a-fA-F\d][a-fA-F\d]"

SAFE_SEGMENT_CHARS = ":@-._~!$&'()*+,;="


class Path(Encodable):
    def __init__(self, pathstr: str) -> None:
        self.segments: list[str] = self._load(pathstr)

    def _load(self, pathstr: str):
        path_segments = pathstr.split("/")
        return self._process_segments([], path_segments)

    def _process_segments(
        self,
        source: list[str],
        to_append: list[str],
    ):
        segments = list(source)
        for seg in to_append:
            if not is_valid_encoded_path.match(seg):
                seg = quote(utf8(seg))
            segments.append(seg)
        return [
            unquote(item.decode("utf-8") if isinstance(item, bytes) else item)
            for item in segments
        ]

    def encode(self):
        return "/".join(quote(utf8(item), SAFE_SEGMENT_CHARS) for item in self.segments)

    def add(self, path: Union[str, "Path"]):
        segments = []
        if isinstance(path, str):
            segments.extend(self._process_segments([], path.lstrip("/").split("/")))
        else:
            segments.extend(path.segments)
        self.segments = self._process_segments(self.segments, segments)
        return self

    def set(self, path: Union[str, "Path"]):
        segments = []
        if isinstance(path, str):
            segments.extend(self._process_segments([], path.split("/")))
        else:
            segments.extend(path.segments)
        self.segments = segments
        return self

    @property
    def isdir(self):
        """Whether this path is a directory.
        Path is considered a directory if is empty or
        if ends with trailing slash

        Returns:
            [type]: [description]
        """
        return not self.segments or (self.segments[-1] == "")

    @property
    def isfile(self):
        return not self.isdir

    def normalize(self):
        if resolved := self.encode():
            normalized = normalize(resolved)
            self.segments = self._load(normalized)
        return self


_duplicates_regex = re.compile(r"/+")


def normalize(path: str) -> str:
    stack = []
    path = _duplicates_regex.sub("/", path)
    for segment in path.split("/"):
        if segment == "..":
            if stack:
                stack.pop()
        elif segment not in [".", ""]:
            stack.append(segment)
        elif segment == ".":
            continue
    return "/" + "/".join(stack) + ("/" * path.endswith("/")) if stack else "/"
