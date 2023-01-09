import pytest

from gyver.database.query._helpers import retrieve_attr
from gyver.database.query.exc import FieldNotFound

from .mocks import Another
from .mocks import PersonAddress
from .mocks import RelatedPerson
from .mocks import mock_table


def test_retrieve_attr_returns_valid_attr():
    assert Another.name == retrieve_attr(Another, "name")
    assert Another.id_ == retrieve_attr(Another, "id")


def test_retrieve_attr_retrieves_attribute_from_table():
    assert mock_table.c.id == retrieve_attr(mock_table, "id")


def test_retrive_attr_raises_field_not_found_if_field_is_invalid():
    with pytest.raises(FieldNotFound):
        retrieve_attr(Another, "invalid")

    with pytest.raises(FieldNotFound):
        retrieve_attr(mock_table, "invalid")


def test_retrieve_attr_returns_any_layer_of_attr_from_relation():
    assert PersonAddress.id_ == retrieve_attr(RelatedPerson, "address.id")
    assert (
        Another.name
        == retrieve_attr(RelatedPerson, "address.another.name")
        == retrieve_attr(PersonAddress, "another.name")
    )


def test_retrieve_attr_raises_error_if_layer_has_invalid_field():
    with pytest.raises(FieldNotFound):
        retrieve_attr(RelatedPerson, "address.invalid.name")

    with pytest.raises(FieldNotFound):
        retrieve_attr(RelatedPerson, "address.another.invalid")

    with pytest.raises(FieldNotFound):
        retrieve_attr(RelatedPerson, "invalid.id")

    with pytest.raises(FieldNotFound):
        retrieve_attr(mock_table, "invalid.invalid")
