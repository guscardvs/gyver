from urllib.parse import quote

from gyver.url.encode import Encodable
from gyver.url.utils import is_valid_encoded_path
from gyver.url.utils import utf8


class Fragment(Encodable):
    def __init__(self, fragment_str: str) -> None:
        self.set(fragment_str)

    def encode(self):
        return self.fragment_str

    def set(self, fragment_str: str):
        if not is_valid_encoded_path.match(fragment_str):
            fragment_str = quote(utf8(fragment_str))
        self.fragment_str = fragment_str
        return self

    def __str__(self):
        return self.fragment_str
