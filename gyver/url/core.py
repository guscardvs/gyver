from collections import defaultdict
from typing import Mapping
from typing import Optional
from urllib.parse import urlparse
from urllib.parse import urlunsplit

from gyver.url.encode import Encodable
from gyver.url.fragment import Fragment
from gyver.url.netloc import Netloc
from gyver.url.path import Path
from gyver.url.query import Query


class URL(Encodable):
    def __init__(self, val: str) -> None:
        self.load(val)

    def load(self, val: str):
        parsed = urlparse(val)
        (
            self.scheme,
            netloc,
            path,
            _,
            query,
            fragment,
        ) = parsed
        self.query = Query(query)
        self.path = Path(path)
        self.port = parsed.port
        self.fragment = Fragment(fragment)
        self.netloc = Netloc(netloc)

    def encode(self, omit_empty_equal: bool = True):
        resolved_query = (
            self.query.encode()
            if omit_empty_equal
            else self.query.omit_empty_equal()
        )
        return urlunsplit(
            (
                self.scheme,
                self.netloc.encode(),
                self.path.encode(),
                resolved_query,
                self.fragment.encode(),
            )
        )

    def __repr__(self) -> str:
        return object.__repr__(self)

    def add(
        self,
        queryasdict: Optional[Mapping[str, str]] = None,
        /,
        path: Optional[str] = None,
        query: Optional[Mapping[str, str]] = None,
        fragment: Optional[str] = None,
        netloc: Optional[str] = None,
        netloc_args: Optional[Netloc] = None,
    ):
        if queryasdict:
            self.query.add(queryasdict)
        if path:
            self.path.add(path)
        if query:
            self.query.add(query)
        if fragment:
            self.fragment.set(fragment)
        if netloc:
            self.netloc.set(netloc)
        if netloc_args:
            self.netloc = self.netloc.merge(netloc_args)
        return self

    def set(
        self,
        queryasdict: Optional[Mapping[str, str]] = None,
        /,
        path: Optional[str] = None,
        query: Optional[Mapping[str, str]] = None,
        fragment: Optional[str] = None,
        netloc: Optional[str] = None,
        netloc_args: Optional[Netloc] = None,
    ):
        if queryasdict:
            self.query.set(queryasdict)
        if path:
            self.path.set(path)
        if query:
            self.query.set(query)
        if fragment:
            self.fragment.set(fragment)
        if netloc:
            self.netloc.set(netloc)
        if netloc_args:
            self.netloc = netloc_args
        return self

    def copy(self):
        new_url = URL("")
        new_url.scheme = self.scheme
        new_url.fragment.fragment_str = self.fragment.fragment_str
        new_url.path.segments = self.path.segments.copy()
        new_url.query.params = defaultdict(
            list,
            ((key, list(value)) for key, value in self.query.params.items()),
        )
        new_url.add(netloc_args=self.netloc)
        return new_url
