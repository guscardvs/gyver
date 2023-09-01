import pytest

from gyver.model import Model, v1
from lazyfields import asynclazyfield, lazyfield, setlazy, force_set

from pydantic_core import ValidationError


def test_model_configs_are_expected():
    class Person(Model):
        name: str
        some_attr_: str

        @lazyfield
        def some_field(self):
            return "hello"

    person = Person(name="my-name", some_attr_="my-attr")

    assert Person.model_fields["some_attr_"].alias == "someAttr"
    assert "some_field" not in Person.model_fields

    with pytest.raises(ValidationError):
        person.name = "other-name"


async def test_model_works_correctly_with_lazyfield():
    class TestModel(Model):
        @lazyfield
        def test(self):
            return "hello"

        @asynclazyfield
        async def atest(self):
            return "world"

    model = TestModel()

    assert model.test == "hello"
    assert await model.atest() == "world"

    force_set(model, "test", "world")
    setlazy(model, "atest", "hello", bypass_setattr=True)

    assert model.test == "world"
    assert await model.atest() == "hello"


def test_v1_support_still_works_correctly_for_model_config():
    class Person(v1.Model):
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


async def test_v1_support_still_works_correctly_for_lazyfield():
    class TestModel(v1.Model):
        @lazyfield
        def test(self):
            return "hello"

        @asynclazyfield
        async def atest(self):
            return "world"

    model = TestModel()

    assert model.test == "hello"
    assert await model.atest() == "world"

    force_set(model, "test", "world")
    setlazy(model, "atest", "hello", bypass_setattr=True)

    assert model.test == "world"
    assert await model.atest() == "hello"
