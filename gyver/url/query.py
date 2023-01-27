from collections import defaultdict
from typing import Mapping
from typing import Optional
from urllib.parse import parse_qs
from urllib.parse import quote

from gyver.url.encode import Encodable


class Query(Encodable):
    def __init__(self, querystr: str) -> None:
        self.params = defaultdict[str, list[str]](list)
        self.params.update(parse_qs(querystr, keep_blank_values=True))

    def encode(self):
        return "&".join(
            "=".join(map(quote, (key, item or "")))
            for key, value in self.params.items()
            for item in value
        )

    def omit_empty_equal(self):
        return "&".join(
            "=".join(map(quote, (key, item))) if item else quote(key)
            for key, value in self.params.items()
            for item in value
        )

    def add(self, args: Optional[Mapping[str, str]] = None, /, **params: str):
        query = {**(args or {}), **params}
        for key, value in query.items():
            self.params[key].append(value)
        return self

    def set(self, args: Optional[Mapping[str, str]] = None, /, **params: str):
        query = {**(args or {}), **params}
        self.params.clear()
        self.add(query)
        return self

    def __setitem__(self, key: str, value: str):
        self.add({key: value})

    def __getitem__(self, key: str) -> list[str]:
        return self.params[key]

    def remove(self, *keys: str):
        for key in keys:
            self.params.pop(key, None)

    def sort(self):
        self.params = dict(sorted(self.params.items()))
