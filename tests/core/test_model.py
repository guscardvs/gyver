import pytest

from core.model import Model
from core.utils import lazyfield


def test_model_configs_are_expected():
    class Person(Model):
        name: str
        some_attr: str

        @lazyfield
        def some_field(self):
            return "hello"

    person = Person(name="my-name", some_attr="my-attr")

    assert Person.__fields__["some_attr"].alias == "someAttr"
    assert "some_field" not in Person.__fields__

    with pytest.raises(TypeError):
        person.name = "other-name"
