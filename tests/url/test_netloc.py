from gyver.url.netloc import Netloc


def test_netloc():  # sourcery skip: extract-duplicate-method
    # Test basic netloc
    netloc = Netloc("www.example.com")
    assert netloc.encode() == "www.example.com"
    assert netloc.host == "www.example.com"
    assert netloc.username is None
    assert netloc.password is None
    assert netloc.port is None

    # Test netloc with port
    netloc = Netloc("www.example.com:8080")
    assert netloc.encode() == "www.example.com:8080"
    assert netloc.host == "www.example.com"
    assert netloc.username is None
    assert netloc.password is None
    assert netloc.port == 8080

    # Test netloc with username and password
    netloc = Netloc("username:password@www.example.com")
    assert netloc.encode() == "username:password@www.example.com"
    assert netloc.host == "www.example.com"
    assert netloc.username == "username"
    assert netloc.password == "password"
    assert netloc.port is None
