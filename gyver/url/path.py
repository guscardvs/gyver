import re
from typing import Union
from urllib.parse import quote, unquote

from typing_extensions import Self

from gyver.attrs import mutable
from gyver.url.encode import Encodable
from gyver.url.utils import is_valid_encoded_path, utf8

PERCENT_REGEX = r"\%[a-fA-F\d][a-fA-F\d]"

SAFE_SEGMENT_CHARS = ":@-._~!$&'()*+,;="


@mutable(eq=False)
class Path(Encodable):
    """Represents a path in a URL.

    Attributes:
        segments (list[str]): List of path segments.
    """

    segments: list[str]

    def __init__(self, pathstr: str) -> None:
        """Initialize a Path object.

        Args:
            pathstr (str): The string representation of the path.
        """
        self.segments = self._load(pathstr)

    def _load(self, pathstr: str) -> list[str]:
        """Load the path segments from the path string.

        Args:
            pathstr (str): The string representation of the path.

        Returns:
            list[str]: List of path segments.
        """
        path_segments = pathstr.split("/")
        return self._process_segments([], path_segments)

    def _process_segments(
        self,
        source: list[str],
        to_append: list[str],
    ) -> list[str]:
        """Process the path segments.

        Args:
            source (list[str]): The source list of segments.
            to_append (list[str]): The list of segments to append.

        Returns:
            list[str]: The processed list of segments.
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

    def encode(self) -> str:
        """Encode the path segments into a URL-encoded string.

        Returns:
            str: The URL-encoded path string.
        """
        return "/".join(quote(utf8(item), SAFE_SEGMENT_CHARS) for item in self.segments)

    def add(self, path: Union[str, "Path"]) -> Self:
        """Add path segments to the existing path.

        Args:
            path (Union[str, Path]): The path segments to add. Can be a string or a Path object.

        Returns:
            Path: The modified Path object.
        """
        segments = []
        if isinstance(path, str):
            segments.extend(self._process_segments([], path.lstrip("/").split("/")))
        else:
            segments.extend(path.segments)
        self.segments = self._process_segments(self.segments, segments)
        return self

    def set(self, path: Union[str, "Path"]) -> Self:
        """Set the path segments to a new value.

        Args:
            path (Union[str, Path]): The new path segments. Can be a string or a Path object.

        Returns:
            Path: The modified Path object.
        """
        segments = []
        if isinstance(path, str):
            segments.extend(self._process_segments([], path.split("/")))
        else:
            segments.extend(path.segments)
        self.segments = segments
        return self

    @property
    def isdir(self) -> bool:
        """Check if the path represents a directory.

        Path is considered a directory if it is empty or ends with a trailing slash.

        Returns:
            bool: True if the path is a directory, False otherwise.
        """
        return not self.segments or (self.segments[-1] == "")

    @property
    def isfile(self) -> bool:
        """Check if the path represents a file.

        Returns:
            bool: True if the path is a file, False if it is a directory.
        """
        return not self.isdir

    def normalize(self) -> Self:
        """Normalize the path by removing redundant segments.

        Returns:
            Path: The normalized Path object.
        """
        if resolved := self.encode():
            normalized = normalize(resolved)
            self.segments = self._load(normalized)
        return self

    def copy(self) -> "Path":
        path = object.__new__(Path)
        path.segments = self.segments.copy()
        return path


_duplicates_regex = re.compile(r"/+")


def normalize(path: str) -> str:
    """Normalize a path string by removing redundant segments.

    Args:
        path (str): The path string to normalize.

    Returns:
        str: The normalized path string.
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
