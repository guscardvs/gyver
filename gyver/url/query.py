from collections import defaultdict
from typing import Mapping
from typing import Optional
from urllib.parse import parse_qs
from urllib.parse import quote

from gyver.attrs import mutable

from gyver.url.encode import Encodable


@mutable(eq=False)
class Query(Encodable):
    """
    Represents a query string and provides methods to manipulate and encode it.

    :param querystr: The input query string.
    """

    params: defaultdict[str, list[str]]

    def __init__(self, querystr: str) -> None:
        """
        Initializes the Query object with the provided query string.

        :param querystr: The input query string to parse.
        """
        self.params = defaultdict(list)
        self.params |= parse_qs(querystr, keep_blank_values=True)

    def encode(self) -> str:
        """
        Encodes the query object into a string representation.

        :return: The encoded query string.
        """
        return "&".join(
            "=".join((quote(key, safe=""), quote(item or "", safe="")))
            for key, value in self.params.items()
            for item in value
        )

    def omit_empty_equal(self) -> str:
        """
        Encodes the query object into a string representation, omitting the equal sign if a value is empty.

        :return: The encoded query string.
        """
        return "&".join(
            "=".join(map(quote, (key, item))) if item else quote(key)
            for key, value in self.params.items()
            for item in value
        )

    def add(
        self, args: Optional[Mapping[str, str]] = None, /, **params: str
    ) -> "Query":
        """
        Adds query parameters to the Query object.

        :param args: Additional query parameters as a mapping object.
        :param params: Additional query parameters as keyword arguments.
        :return: The modified Query object.
        """
        query = {**(args or {}), **params}
        for key, value in query.items():
            self.params[key].append(value)
        return self

    def set(
        self, args: Optional[Mapping[str, str]] = None, /, **params: str
    ) -> "Query":
        """
        Sets the query parameters, replacing any existing parameters.

        :param args: New query parameters as a mapping object.
        :param params: New query parameters as keyword arguments.
        :return: The modified Query object.
        """
        query = {**(args or {}), **params}
        self.params.clear()
        self.add(query)
        return self

    def __setitem__(self, key: str, value: str) -> None:
        """
        Sets a query parameter using the square bracket syntax.

        :param key: The parameter key.
        :param value: The parameter value.
        """
        self.add({key: value})

    def __getitem__(self, key: str) -> list[str]:
        """
        Retrieves the values of a query parameter using the square bracket syntax.

        :param key: The parameter key.
        :return: The list of parameter values.
        """
        return self.params[key]

    def remove(self, *keys: str) -> "Query":
        """
        Removes query parameters from the Query object.

        :param keys: The parameter keys to remove.
        :return: The modified Query object.
        """
        for key in keys:
            self.params.pop(key, None)
        return self

    def sort(self) -> "Query":
        """
        Sorts the query parameters in lexicographic order based on the parameter names.

        :return: The modified Query object.
        """
        self.params = defaultdict(list, sorted(self.params.items()))
        return self
