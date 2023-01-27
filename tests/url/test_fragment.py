from gyver.url.fragment import Fragment


def test_fragment():
    # Test creating a fragment from a string
    fragment = Fragment("test")
    assert fragment.encode() == "test"

    # Test encoding a fragment with special characters
    fragment = Fragment("test#test")
    assert fragment.encode() == "test%23test"

    # Test encoding with encoded does not double encodes
    fragment = Fragment("test%23test")
    assert fragment.encode() == "test%23test"

    # Test updating a fragment
    fragment.set("new")
    assert fragment.encode() == "new"
