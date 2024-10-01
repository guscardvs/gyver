from collections.abc import Mapping
from urllib.parse import urlparse, urlunsplit

from typing_extensions import Self

from gyver.attrs import mutable
from gyver.url.encode import Encodable
from gyver.url.fragment import Fragment
from gyver.url.netloc import Netloc
from gyver.url.path import Path
from gyver.url.query import Query


@mutable(eq=False)
class URL(Encodable):
    """Class representing a URL object.

    Attributes:
        scheme (str): The URL scheme.
        netloc (Netloc): The URL netloc.
        path (Path): The URL path.
        query (Query): The URL query parameters.
        fragment (Fragment): The URL fragment.
    """

    scheme: str
    netloc: Netloc
    path: Path
    query: Query
    fragment: Fragment

    def __init__(self, val: str) -> None:
        """Initialize a URL object.

        Args:
            val (str): The URL string.
        """
        self.load(val)

    def load(self, val: str):
        """Parse the given URL string and populate the properties of the URL object.

        Args:
            val (str): The URL string.
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

    def encode(self, append_empty_equal: bool = True) -> str:
        """Encode the URL object as a URL string.

        Args:
            append_empty_equal (bool, optional): Whether to append empty values with an equal sign in the query string.

        Returns:
            str: The encoded URL string.
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
        queryasdict: Mapping[str, str] | None = None,
        /,
        path: str | None = None,
        query: Mapping[str, str] | None = None,
        fragment: str | None = None,
        netloc: str | None = None,
        netloc_obj: Netloc | None = None,
        scheme: str | None = None,
    ) -> Self:
        """Add components to the URL.

        Args:
            queryasdict (Optional[Mapping[str, str]], optional): Dictionary-like object representing query parameters.
            path (Optional[str], optional): Path string to add to the URL.
            query (Optional[Mapping[str, str]], optional): Dictionary-like object representing additional query parameters.
            fragment (Optional[str], optional): Fragment string to set for the URL.
            netloc (Optional[str], optional): Netloc string to set for the URL.
            netloc_obj (Optional[Netloc], optional): Netloc object to merge with the existing netloc.
            scheme (Optional[str], optional): Scheme to set for the URL.

        Returns:
            URL: The updated URL object.
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
        queryasdict: Mapping[str, str] | None = None,
        /,
        path: str | None = None,
        query: Mapping[str, str] | None = None,
        fragment: str | None = None,
        netloc: str | None = None,
        netloc_obj: Netloc | None = None,
        scheme: str | None = None,
    ) -> Self:
        """Set components of the URL.

        Args:
            queryasdict (Optional[Mapping[str, str]], optional): Dictionary-like object representing query parameters.
            path (Optional[str], optional): Path string to set for the URL.
            query (Optional[Mapping[str, str]], optional): Dictionary-like object representing query parameters.
            fragment (Optional[str], optional): Fragment string to set for the URL.
            netloc (Optional[str], optional): Netloc string to set for the URL.
            netloc_obj (Optional[Netloc], optional): Netloc object to set as the netloc.
            scheme (Optional[str], optional): Scheme to set for the URL.

        Returns:
            URL: The updated URL object.
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

    def copy(self) -> "URL":
        """Create a copy of the URL object.

        Returns:
            URL: The copied URL object.
        """
        url = object.__new__(type(self))
        url.scheme = self.scheme
        url.netloc = self.netloc.copy()
        url.path = self.path.copy()
        url.query = self.query.copy()
        url.fragment = self.fragment.copy()
        return url

    @classmethod
    def from_netloc(
        cls,
        netloc: Netloc | None = None,
        *,
        username: str | None = None,
        password: str | None = None,
        host: str | None = None,
        port: int | None = None,
    ) -> Self:
        """Create a URL object from a netloc.

        Args:
            netloc (Optional[Netloc], optional): Netloc object to set for the URL.
            username (Optional[str], optional): Username for the netloc.
            password (Optional[str], optional): Password for the netloc.
            host (Optional[str], optional): Host for the netloc.
            port (Optional[int], optional): Port for the netloc.

        Returns:
            URL: The URL object created from the netloc.
        """
        url = cls("")
        newnetloc = Netloc.from_args(host or "", username, password, port)
        if netloc:
            newnetloc = netloc.merge(newnetloc)
        url.add(netloc_obj=newnetloc)
        return url

    @classmethod
    def from_args(
        cls,
        queryasdict: Mapping[str, str] | None = None,
        /,
        path: str | None = None,
        query: Mapping[str, str] | None = None,
        fragment: str | None = None,
        netloc: str | None = None,
        netloc_obj: Netloc | None = None,
        scheme: str | None = None,
    ):
        url = URL("")
        url.set(
            queryasdict,
            path,
            query,
            fragment,
            netloc,
            netloc_obj,
            scheme,
        )
        return url
