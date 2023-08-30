# Model

`Model` is an abstract class used to create python objects with a few opinions.
It is built entirely using `pydantic.BaseModel` and `orjson` for json parsing.
By default all Model classes are:

* frozen
* with from_attributes enabled
* with populate_by_name enabled
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

## Compatibility

`Model` is updated to work with `pydantic>=2.0.0`, 
however it will still hold compatibility to v1 
and if you are using v2 but haven't upgraded all of the code,
you can find the old model at `gyver.model.v1`

