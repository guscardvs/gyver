from typing import Optional
from urllib.parse import quote

from gyver.attrs import mutable

from gyver.url.encode import Encodable
from gyver.url.utils import utf8


@mutable(eq=False)
class Netloc(Encodable):
    """
    Represents the network location portion of a URL.

    :param netloc: The network location string to initialize the `Netloc` object.
    :type netloc: str

    :ivar username: The username for authentication.
    :vartype username: Optional[str]
    :ivar password: The password for authentication.
    :vartype password: Optional[str]
    :ivar host: The host name or IP address.
    :vartype host: str
    :ivar port: The port number.
    :vartype port: Optional[int]

    Examples:
        >>> netloc = Netloc("user:pass@example.com:8080")
        >>> netloc.username
        'user'
        >>> netloc.password
        'pass'
        >>> netloc.host
        'example.com'
        >>> netloc.port
        8080
    """

    username: Optional[str]
    password: Optional[str]
    host: str
    port: Optional[int]

    def __init__(self, netloc: str) -> None:
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        self.load(netloc)

    def load(self, netloc: str):
        """
        Load the network location from the given netloc string.

        :param netloc: The network location string.
        :type netloc: str

        :return: None

        Examples:
            >>> netloc = Netloc("")
            >>> netloc.load("user:pass@example.com:8080")
            >>> netloc.username
            'user'
            >>> netloc.password
            'pass'
            >>> netloc.host
            'example.com'
            >>> netloc.port
            8080
        """
        userinfo, _, host = netloc.partition("@")
        port = None
        if host:
            username, _, password = userinfo.partition(":")
            self.username = username
            self.password = password
        else:
            host = userinfo
        if ":" in host:
            host, _, port = host.partition(":")
        self.host = host
        port = int(port) if port else None
        self.port = port

    def encode(self):
        """
        Encode the network location into a string.

        :return: The encoded network location string.
        :rtype: str
        """
        netloc = ""
        if self.username:
            netloc = f"{quote(utf8(self.username))}"
            if self.password:
                netloc += f":{quote(utf8(self.password))}"
            netloc += "@"
        netloc += self.host
        if self.port:
            netloc += f":{self.port}"
        return netloc

    def parse(self, netloc: str):
        """
        Parse the given netloc string and populate the properties of the Netloc object.

        :param netloc: The netloc string to parse.
        :type netloc: str

        :return: None
        """
        if "@" in netloc:
            userinfo, host = netloc.split("@", 1)
            if ":" in userinfo:
                self.username, self.password = userinfo.split(":", 1)
            else:
                self.username = userinfo
            self.host = host
        elif ":" in netloc:
            self.host, port = netloc.split(":", 1)
            if port:
                self.port = int(port)
        else:
            self.host = netloc

    def set(
        self,
        host: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """
        Set the network location properties.

        :param host: The host name or IP address.
        :type host: Optional[str]
        :param username: The username for authentication.
        :type username: Optional[str]
        :param password: The password for authentication.
        :type password: Optional[str]
        :param port: The port number.
        :type port: Optional[int]

        :return: The updated `Netloc` object.
        :rtype: Netloc
        """
        self.host = host or self.host
        self.username = username or self.username
        self.password = password or self.password
        self.port = port or self.port
        return self

    def merge(self, netloc: "Netloc") -> "Netloc":
        """
        Merge the properties of the given `Netloc` object with the current object.

        :param netloc: The `Netloc` object to merge.
        :type netloc: Netloc

        :return: The merged `Netloc` object.
        :rtype: Netloc
        """
        host = netloc.host or self.host
        username = netloc.username or self.username
        password = netloc.password or self.password
        port = netloc.port or self.port
        return self.from_args(host, username, password, port or None)

    @classmethod
    def from_args(
        cls,
        host: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """
        Create a new `Netloc` object from individual arguments.

        :param host: The host name or IP address.
        :type host: str
        :param username: The username for authentication.
        :type username: Optional[str]
        :param password: The password for authentication.
        :type password: Optional[str]
        :param port: The port number.
        :type port: Optional[int]

        :return: The created `Netloc` object.
        :rtype: Netloc
        """
        netloc = cls("")
        return netloc.set(host, username, password, port)
