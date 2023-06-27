from urllib.parse import quote

from gyver.attrs import mutable

from gyver.url.encode import Encodable
from gyver.url.utils import is_valid_encoded_path
from gyver.url.utils import utf8


@mutable(eq=False)
class Fragment(Encodable):
    """Represents an encodable URL fragment."""

    fragment_str: str

    def __init__(self, fragment_str: str) -> None:
        """
        Initialize the Fragment object.

        :param fragment_str: The fragment string.
        """
        self.set(fragment_str)

    def encode(self):
        """
        Encode the fragment string.

        :return: The encoded fragment string.
        """
        return self.fragment_str

    def set(self, fragment_str: str):
        """
        Set a new fragment string.

        If the provided string is not already encoded, it will be encoded.

        :param fragment_str: The new fragment string.
        :return: self
        """
        if not is_valid_encoded_path.match(fragment_str):
            fragment_str = quote(utf8(fragment_str))
        self.fragment_str = fragment_str
        return self

    def __str__(self):
        """
        Return the fragment string when converting the object to a string.

        :return: The fragment string.
        """
        return self.fragment_str
