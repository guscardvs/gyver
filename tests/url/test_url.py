from gyver.url.core import URL
from gyver.url.core import Netloc
from gyver.url.core import Path
from gyver.url.core import Query


def test_url():
    # Test adding query parameters
    url = URL("https://www.example.com/path?key1=value1")
    url.add(query={"key2": "value2", "key3": "value3"})
    assert url.query == Query("key1=value1&key2=value2&key3=value3")
    assert url == "https://www.example.com/path?key1=value1&key2=value2&key3=value3"

    # Test adding path segments
    url = URL("https://www.example.com/path")
    url.add(path="subpath")
    assert url.path == Path("/path/subpath")
    assert url == "https://www.example.com/path/subpath"

    # Test adding fragment
    url = URL("https://www.example.com/path")
    url.add(fragment="section1")
    assert url.fragment == "section1"
    assert url == "https://www.example.com/path#section1"

    # Test adding netloc
    url = URL("https://www.example.com/path")
    url.add(netloc="www.example2.com")
    assert url.netloc == "www.example2.com"
    assert url == "https://www.example2.com/path"

    # Test adding netloc with username and password
    url = URL("https://www.example.com/path")
    url.add(
        netloc_obj=Netloc.from_args(
            host="www.example2.com",
            username="username",
            password="password",
        )
    )
    assert url.netloc == "username:password@www.example2.com"
    assert url == "https://username:password@www.example2.com/path"

    # Test adding netloc with port
    url = URL("https://www.example.com/path")
    url.add(netloc_obj=Netloc.from_args(host="www.example2.com", port=8080))
    assert url.netloc == "www.example2.com:8080"
    assert url == "https://www.example2.com:8080/path"

    # Test adding multiple components
    url = URL("https://www.example.com/path?key1=value1").add(
        path="subpath",
        query={"key2": "value2", "key3": "value3"},
        fragment="section1",
        netloc_obj=Netloc.from_args(
            host="www.example2.com",
            username="username",
            password="password",
            port=8080,
        ),
    )
    assert url.path == Path("/path/subpath")
    assert url.query == Query("key1=value1&key2=value2&key3=value3")
    assert url.fragment == "section1"
    assert url.netloc == "username:password@www.example2.com:8080"
    assert (
        url == "https://username:password@www.example2.com"
        ":8080/path/subpath?key1=value1&key2=value2&key3=value3#section1"
    )

    # Test copying the url makes the an equal url

    url = URL("https://www.example.com/path?key1=value1").add(
        query={"key2": "value2", "key3": "value3"}
    )
    assert url.encode() == url.copy().encode()

    # Test copying the url returns a new instance
    url = URL("http://www.example.com")
    new_url = url.copy()
    assert new_url is not url

    # Test copying the url does not override any values on the old url
    url = URL("https://www.example.com/path?key1=value1").add(
        query={"key2": "value2", "key3": "value3"}
    )
    new_url = url.copy()
    assert url.path.segments is not new_url.path.segments
    assert url.query.params is not new_url.query.params
