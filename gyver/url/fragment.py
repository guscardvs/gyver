from urllib.parse import quote

from typing_extensions import Self

from gyver.attrs import mutable
from gyver.url.encode import Encodable
from gyver.url.utils import is_valid_encoded_path, utf8


@mutable(eq=False)
class Fragment(Encodable):
    """Represents an encodable URL fragment.

    Attributes:
        fragment_str (str): The fragment string.
    """

    def __init__(self, fragment_str: str) -> None:
        """
        Initialize the Fragment object.

        Args:
            fragment_str (str): The fragment string.
        """
        self.set(fragment_str)

    def encode(self) -> str:
        """
        Encode the fragment string.

        Returns:
            str: The encoded fragment string.
        """
        return self.fragment_str

    def set(self, fragment_str: str) -> Self:
        """
        Set a new fragment string.

        If the provided string is not already encoded, it will be encoded.

        Args:
            fragment_str (str): The new fragment string.

        Returns:
            Fragment: The updated Fragment object.
        """
        if not is_valid_encoded_path.match(fragment_str):
            fragment_str = quote(utf8(fragment_str))
        self.fragment_str = fragment_str
        return self

    def __str__(self) -> str:
        """
        Return the fragment string when converting the object to a string.

        Returns:
            str: The fragment string.
        """
        return self.fragment_str

    def copy(self) -> "Fragment":
        fragment = object.__new__(Fragment)
        fragment.fragment_str = self.fragment_str
        return fragment
