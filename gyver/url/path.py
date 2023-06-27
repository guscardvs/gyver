import re
from typing import Union
from urllib.parse import quote
from urllib.parse import unquote

from gyver.attrs import mutable

from gyver.url.encode import Encodable
from gyver.url.utils import is_valid_encoded_path
from gyver.url.utils import utf8

PERCENT_REGEX = r"\%[a-fA-F\d][a-fA-F\d]"

SAFE_SEGMENT_CHARS = ":@-._~!$&'()*+,;="


@mutable(eq=False)
class Path(Encodable):
    segments: list[str]

    def __init__(self, pathstr: str) -> None:
        """
        Initialize a Path object.

        :param pathstr: The string representation of the path.
        """
        self.segments = self._load(pathstr)

    def _load(self, pathstr: str):
        """
        Load the path segments from the path string.

        :param pathstr: The string representation of the path.
        :return: The list of path segments.
        """
        path_segments = pathstr.split("/")
        return self._process_segments([], path_segments)

    def _process_segments(
        self,
        source: list[str],
        to_append: list[str],
    ):
        """
        Process the path segments.

        :param source: The source list of segments.
        :param to_append: The list of segments to append.
        :return: The processed list of segments.
        """
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
        """
        Encode the path segments into a URL-encoded string.

        :return: The URL-encoded path string.
        """
        return "/".join(quote(utf8(item), SAFE_SEGMENT_CHARS) for item in self.segments)

    def add(self, path: Union[str, "Path"]):
        """
        Add path segments to the existing path.

        :param path: The path segments to add. Can be a string or a Path object.
        :return: The modified Path object.
        """
        segments = []
        if isinstance(path, str):
            segments.extend(self._process_segments([], path.lstrip("/").split("/")))
        else:
            segments.extend(path.segments)
        self.segments = self._process_segments(self.segments, segments)
        return self

    def set(self, path: Union[str, "Path"]):
        """
        Set the path segments to a new value.

        :param path: The new path segments. Can be a string or a Path object.
        :return: The modified Path object.
        """
        segments = []
        if isinstance(path, str):
            segments.extend(self._process_segments([], path.split("/")))
        else:
            segments.extend(path.segments)
        self.segments = segments
        return self

    @property
    def isdir(self):
        """
        Check if the path represents a directory.

        Path is considered a directory if it is empty or ends with a trailing slash.

        :return: True if the path is a directory, False otherwise.
        """
        return not self.segments or (self.segments[-1] == "")

    @property
    def isfile(self):
        """
        Check if the path represents a file.

        :return: True if the path is a file, False if it is a directory.
        """
        return not self.isdir

    def normalize(self):
        """
        Normalize the path by removing redundant segments.

        :return: The normalized Path object.
        """
        if resolved := self.encode():
            normalized = normalize(resolved)
            self.segments = self._load(normalized)
        return self


_duplicates_regex = re.compile(r"/+")


def normalize(path: str) -> str:
    """
    Normalize a path string by removing redundant segments.

    :param path: The path string to normalize.
    :return: The normalized path string.
    """
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
