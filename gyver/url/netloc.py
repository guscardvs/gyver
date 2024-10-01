from urllib.parse import quote

from typing_extensions import Self

from gyver.attrs import mutable
from gyver.url.encode import Encodable
from gyver.url.utils import utf8


@mutable(eq=False)
class Netloc(Encodable):
    """Represents the network location portion of a URL.

    Attributes:
        username (Optional[str]): The username for authentication.
        password (Optional[str]): The password for authentication.
        host (str): The host name or IP address.
        port (Optional[int]): The port number.
    """

    username: str | None
    password: str | None
    host: str
    port: int | None

    def __init__(self, netloc: str) -> None:
        """
        Initialize the Netloc object.

        Args:
            netloc (str): The network location string.
        """
        self.username: str | None = None
        self.password: str | None = None
        self.load(netloc)

    def load(self, netloc: str):
        """
        Load the network location from the given netloc string.

        Args:
            netloc (str): The network location string.
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

    def encode(self) -> str:
        """
        Encode the network location into a string.

        Returns:
            str: The encoded network location string.
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

        Args:
            netloc (str): The netloc string to parse.
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
        host: str | None = None,
        username: str | None = None,
        password: str | None = None,
        port: int | None = None,
    ) -> Self:
        """
        Set the network location properties.

        Args:
            host (Optional[str], optional): The host name or IP address.
            username (Optional[str], optional): The username for authentication.
            password (Optional[str], optional): The password for authentication.
            port (Optional[int], optional): The port number.
        """
        self.host = host or self.host
        self.username = username or self.username
        self.password = password or self.password
        self.port = port or self.port
        return self

    def merge(self, netloc: "Netloc") -> "Netloc":
        """
        Merge the properties of the given `Netloc` object with the current object.

        Args:
            netloc (Netloc): The `Netloc` object to merge.

        Returns:
            Netloc: The merged `Netloc` object.
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
        username: str | None = None,
        password: str | None = None,
        port: int | None = None,
    ) -> Self:
        """
        Create a new `Netloc` object from individual arguments.

        Args:
            host (str): The host name or IP address.
            username (Optional[str], optional): The username for authentication.
            password (Optional[str], optional): The password for authentication.
            port (Optional[int], optional): The port number.

        Returns:
            Netloc: The created `Netloc` object.
        """
        netloc = cls("")
        return netloc.set(host, username, password, port)

    def copy(self) -> "Netloc":
        netloc = object.__new__(type(self))
        netloc.host = self.host
        netloc.username = self.username
        netloc.password = self.password
        netloc.port = self.port
        return netloc
