# Model

`Model` is an abstract class used to create python objects with a few opinions.
It is built entirely using `pydantic.BaseModel` and `orjson` for json parsing.
By default all Model classes are:

* frozen
* with orm_mode enabled
* with allow_population_by_field_name enabled
* with support for all gyver features
* with alias generation for camelCase

## Usage

```python
from gyver.model import Model

class Person(Model):
    name: str
    email: str
    type_: int = 0
```

## Mutable Model

If you need all the features of Model but don't want the immutability,
you can use `gyver.model.MutableModel`
