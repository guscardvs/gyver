from typing import Optional
from urllib.parse import quote

from gyver.url.encode import Encodable
from gyver.url.utils import utf8


class Netloc(Encodable):
    def __init__(self, netloc: str) -> None:
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        self.load(netloc)

    def load(self, netloc: str):
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
        self.host = host or self.host
        self.username = username or self.username
        self.password = password or self.password
        self.port = port or self.port
        return self

    def merge(self, netloc: "Netloc") -> "Netloc":
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
        netloc = cls("")
        return netloc.set(host, username, password, port)
