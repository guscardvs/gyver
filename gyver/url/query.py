from collections import defaultdict
from collections.abc import Mapping
from urllib.parse import parse_qs, quote

from typing_extensions import Self

from gyver.attrs import mutable
from gyver.url.encode import Encodable


@mutable(eq=False)
class Query(Encodable):
    """Represents a query string and provides methods to manipulate and encode it.

    Attributes:
        params (defaultdict[str, list[str]]): The dictionary containing query parameters.
    """

    params: defaultdict[str, list[str]]

    def __init__(self, querystr: str) -> None:
        """Initializes the Query object with the provided query string.

        Args:
            querystr (str): The input query string to parse.
        """
        self.params = defaultdict(list)
        self.params |= parse_qs(querystr, keep_blank_values=True)

    def encode(self) -> str:
        """Encodes the query object into a string representation.

        Returns:
            str: The encoded query string.
        """
        return "&".join(
            "=".join((quote(key, safe=""), quote(item or "", safe="")))
            for key, value in self.params.items()
            for item in value
        )

    def omit_empty_equal(self) -> str:
        """Encodes the query object into a string representation, omitting the equal sign if a value is empty.

        Returns:
            str: The encoded query string.
        """
        return "&".join(
            "=".join(map(quote, (key, item))) if item else quote(key)
            for key, value in self.params.items()
            for item in value
        )

    def add(self, args: Mapping[str, str] | None = None, /, **params: str) -> Self:
        """Adds query parameters to the Query object.

        Args:
            args (Optional[Mapping[str, str]], optional): Additional query parameters as a mapping object.
            **params (str): Additional query parameters as keyword arguments.

        Returns:
            Query: The modified Query object.
        """
        query = {**(args or {}), **params}
        for key, value in query.items():
            self.params[key].append(value)
        return self

    def set(self, args: Mapping[str, str] | None = None, /, **params: str) -> Self:
        """Sets the query parameters, replacing any existing parameters.

        Args:
            args (Optional[Mapping[str, str]], optional): New query parameters as a mapping object.
            **params (str): New query parameters as keyword arguments.

        Returns:
            Query: The modified Query object.
        """
        query = {**(args or {}), **params}
        self.params.clear()
        self.add(query)
        return self

    def __setitem__(self, key: str, value: str) -> None:
        """Sets a query parameter using the square bracket syntax.

        Args:
            key (str): The parameter key.
            value (str): The parameter value.
        """
        self.add({key: value})

    def __getitem__(self, key: str) -> list[str]:
        """Retrieves the values of a query parameter using the square bracket syntax.

        Args:
            key (str): The parameter key.

        Returns:
            list[str]: The list of parameter values.
        """
        return self.params[key]

    def remove(self, *keys: str) -> Self:
        """Removes query parameters from the Query object.

        Args:
            keys (str): The parameter keys to remove.

        Returns:
            Query: The modified Query object.
        """
        for key in keys:
            self.params.pop(key, None)
        return self

    def sort(self) -> Self:
        """Sorts the query parameters in lexicographic order based on the parameter names.

        Returns:
            Query: The modified Query object.
        """
        self.params = defaultdict(list, sorted(self.params.items()))
        return self

    def copy(self) -> "Query":
        query = object.__new__(type(self))
        query.params = self.params.copy()
        return query

    def first(self) -> dict[str, str]:
        """Return a dictionary containing the first value for each query parameter.

        Returns:
            dict[str, str]: A dictionary where keys are query parameter names
                and values are the first values associated with those parameters.
        """
        return {key: value[0] for key, value in self.params.items()}

    def index_or_first(self, idx: int) -> dict[str, str]:
        """Return a dictionary containing the value at index 'idx' for each query parameter,
        or the first value if 'idx' exceeds the length of the parameter's value list.

        Args:
            idx (int): The index to retrieve for each query parameter.

        Returns:
            dict[str, str]: A dictionary where keys are query parameter names
                and values are the values at index 'idx' or the first values
                if 'idx' exceeds the length of the parameter's value list.
        """
        return {
            key: value[0 if len(value) <= idx else idx]
            for key, value in self.params.items()
        }

    def index_or_last(self, idx: int) -> dict[str, str]:
        """Return a dictionary containing the value at index 'idx' for each query parameter,
        or the last value if 'idx' exceeds the length of the parameter's value list.

        Args:
            idx (int): The index to retrieve for each query parameter.

        Returns:
            dict[str, str]: A dictionary where keys are query parameter names
                and values are the values at index 'idx' or the last values
                if 'idx' exceeds the length of the parameter's value list.
        """
        return {
            key: value[-1 if len(value) <= idx else idx]
            for key, value in self.params.items()
        }
