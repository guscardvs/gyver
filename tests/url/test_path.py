from gyver.url.path import Path


def test_normalize_path():
    # Test case 1: Basic usage
    assert Path("/a//./b/..//c/").normalize().encode() == "/a/c/"

    # Test case 2: Handling segments starting with '.'
    assert Path("//a/.b///c//").normalize().encode() == "/a/.b/c/"

    # Test case 3: Handling multiple ".." and "." segments
    assert (
        Path("/a/b/c/d/e/f/../g/./h/i/j/").normalize().encode() == "/a/b/c/d/e/g/h/i/j/"
    )

    # Test case 4: Handling an empty path
    assert Path("").normalize().encode() == ""

    # Test case 5: Handling a single "/"
    assert Path("/").normalize().encode() == "/"

    # Test case 6: Handling multiple "/"
    assert Path("////a/b/c/d").normalize().encode() == "/a/b/c/d"

    # Test case 7: Handling multiple segments starting with '.'
    assert Path("/.b/.c/.d/e/").normalize().encode() == "/.b/.c/.d/e/"


def test_path():
    # Test basic initialization
    path = Path("/path/to/file")
    assert path.segments == ["", "path", "to", "file"]

    # Test encoding
    assert path.encode() == "/path/to/file"

    # Test adding a path
    path.add("/another/path")
    assert path.segments == ["", "path", "to", "file", "another", "path"]
    assert path.encode() == "/path/to/file/another/path"

    # Test setting a path
    path.set("/new/path")
    assert path.segments == ["", "new", "path"]
    assert path.encode() == "/new/path"

    # Test isdir property
    path = Path("/path/to/")
    assert path.isdir
    path = Path("/path/to/file")
    assert not path.isdir

    # Test isfile property
    path = Path("/path/to/")
    assert not path.isfile
    path = Path("/path/to/file")
    assert path.isfile

    # Test normalize
    path = Path("/path/to/file/../another/path/")
    path.normalize()
    assert path.segments == ["", "path", "to", "another", "path", ""]
    assert path.encode() == "/path/to/another/path/"

    # Test empty str on Path
    path = Path("")

    assert path.segments == [""]
    assert path.encode() == ""

    # Test with a single forward slash
    path = Path("/")

    assert path.segments == ["", ""]
    assert path.encode() == "/"

    # Test with a lot of slashes
    path = Path("////a////b//")

    assert path.segments == ["", "", "", "", "a", "", "", "", "b", "", ""]

    # Test if path encodes correctly
    path = Path("/a b/c d/")

    assert path.encode() == "/a%20b/c%20d/"

    # Test if path does not overencodes string
    path = Path("/a%20b/c%20d/")

    assert path.encode() == "/a%20b/c%20d/"
