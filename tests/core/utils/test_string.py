from core.utils import string


def test_to_camel_should_return_expected_string():
    vals = (
        ("my_string", "myString"),
        ("myOtherString", "myOtherString"),
        ("another_string_name", "anotherStringName"),
        ("type_", "type"),
    )
    for val, expected in vals:
        assert string.to_camel(val) == expected


def test_to_snake_should_return_expected_string():
    vals = (
        ("myString", "my_string"),
        ("myOtherString", "my_other_string"),
        ("AnotherStringName", "another_string_name"),
        ("MYName", "myname"),
        ("string_a", "string_a"),
    )
    for val, expected in vals:
        assert string.to_snake(val) == expected


def test_upper_camel_should_return_expected_string():
    vals = (
        ("my_string", "MyString"),
        ("myOtherString", "MyOtherString"),
        ("another_string_name", "AnotherStringName"),
        ("type_", "Type"),
    )
    for val, expected in vals:
        assert string.upper_camel(val) == expected
