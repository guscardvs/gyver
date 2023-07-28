from collections import defaultdict
from typing import Mapping
from typing import Optional
from urllib.parse import urlparse
from urllib.parse import urlunsplit

from gyver.attrs import mutable

from gyver.url.encode import Encodable
from gyver.url.fragment import Fragment
from gyver.url.netloc import Netloc
from gyver.url.path import Path
from gyver.url.query import Query


@mutable(eq=False)
class URL(Encodable):
    scheme: str
    netloc: Netloc
    path: Path
    query: Query
    fragment: Fragment

    def __init__(self, val: str) -> None:
        self.load(val)

    def load(self, val: str):
        """
        Parse the given URL string and populate the properties of the URL object.

        :param val: The URL string.
        """
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
        self.fragment = Fragment(fragment)
        self.netloc = Netloc(netloc)

    def encode(self, append_empty_equal: bool = True):
        """
        Encode the URL object as a URL string.

        :param append_empty_equal: Whether to append empty values with an equal sign in the query string.
        :return: The encoded URL string.
        """
        resolved_query = (
            self.query.encode() if append_empty_equal else self.query.omit_empty_equal()
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

    def add(
        self,
        queryasdict: Optional[Mapping[str, str]] = None,
        /,
        path: Optional[str] = None,
        query: Optional[Mapping[str, str]] = None,
        fragment: Optional[str] = None,
        netloc: Optional[str] = None,
        netloc_obj: Optional[Netloc] = None,
        scheme: Optional[str] = None,
    ):
        """
        Add components to the URL.

        :param queryasdict: Dictionary-like object representing query parameters.
        :param path: Path string to add to the URL.
        :param query: Dictionary-like object representing additional query parameters.
        :param fragment: Fragment string to set for the URL.
        :param netloc: Netloc string to set for the URL.
        :param netloc_obj: Netloc object to merge with the existing netloc.
        :return: The updated URL object.
        """
        if queryasdict:
            self.query.add(queryasdict)
        if path:
            self.path.add(path)
        if query:
            self.query.add(query)
        if fragment:
            self.fragment.set(fragment)
        if netloc:
            self.netloc = self.netloc.merge(Netloc(netloc))
        if netloc_obj:
            self.netloc = self.netloc.merge(netloc_obj)
        if scheme:
            self.scheme = scheme
        return self

    def set(
        self,
        queryasdict: Optional[Mapping[str, str]] = None,
        /,
        path: Optional[str] = None,
        query: Optional[Mapping[str, str]] = None,
        fragment: Optional[str] = None,
        netloc: Optional[str] = None,
        netloc_obj: Optional[Netloc] = None,
        scheme: Optional[str] = None,
    ):
        """
        Set components of the URL.

        :param queryasdict: Dictionary-like object representing query parameters.
        :param path: Path string to set for the URL.
        :param query: Dictionary-like object representing query parameters.
        :param fragment: Fragment string to set for the URL.
        :param netloc: Netloc string to set for the URL.
        :param netloc_obj: Netloc object to set as the netloc.
        :return: The updated URL object.
        """
        if queryasdict:
            self.query.set(queryasdict)
        if path:
            self.path.set(path)
        if query:
            self.query.set(query)
        if fragment:
            self.fragment.set(fragment)
        if netloc:
            self.netloc.load(netloc)
        if netloc_obj:
            self.netloc = netloc_obj
        if scheme:
            self.scheme = scheme
        return self

    def copy(self):
        """
        Create a copy of the URL object.

        :return: The copied URL object.
        """
        new_url = URL("")
        new_url.scheme = self.scheme
        new_url.fragment.fragment_str = self.fragment.fragment_str
        new_url.path.segments = self.path.segments.copy()
        new_url.query.params = defaultdict(
            list,
            ((key, list(value)) for key, value in self.query.params.items()),
        )
        new_url.add(netloc_obj=self.netloc)
        return new_url

    @classmethod
    def from_netloc(
        cls,
        netloc: Optional[Netloc] = None,
        *,
        username: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        url = cls("")
        newnetloc = Netloc.from_args(host or "", username, password, port)
        if netloc:
            newnetloc = netloc.merge(newnetloc)
        url.add(netloc_obj=newnetloc)
        return url
