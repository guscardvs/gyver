# Utils
Utils is a module with a lot of functions and classes for diverse use cases and does not depend on any libraries or gyver features.

## Exceptions

[gyver.utils.exc][] has a single function:

* `def panic(exc: type[ExceptionT], message: str, *args) -> ExceptionT`:
   `panic` instantiates the `exc` class with `message` and as its first parameter with an exclamation mark appended to it and the rest of the `*args`. If `message` already endswith an exclamation mark, panic will overwrite it.

```python
from gyver.utils import panic

# raises IndexError with first arg as "Index should be 1!"
raise panic(IndexError, "Index should be 1")
```


## Finder

[gyver.utils.finder][] provides an interface to search for and import specific entities (defined by a user-provided validator function) from a codebase. This can be useful if you need to load dynamically entities into the namespace, for example, in a migration script.

By default, Gyver ships with two validators:

- `instance_validator(*types: type)`: When used with `Finder`, this selects entities that are instances of any of the `types` provided.
- `class_validator(*types: type)`: When used with `Finder`, this selects entities that inherit from any of the `types` provided. The `class_validator` excludes the parent class itself from the match.

### Example:

```python
from gyver.utils import FinderBuilder
from pathlib import Path

MY_ROOT_DIR = Path(__file__).parent

class MyClass:
  def __init__(self):
    self.value = 1

# Create a Finder instance using instance_validator, passing
# your desired class(es) as its parameter and the root dir.
# Your root dir will be used to import. For example: my_root_dir.mymod.myclass_instance
finder = (
  FinderBuilder()
  .instance_of(MyClass)
  .from_path(MY_ROOT_DIR)
  .build()
)

# Run finder.find() to search for the instances.
# After this step, your instances are already loaded in the namespace.
output = finder.find()

# If you actually need to handle the output,
# the output mapping is [modname: str, instance: instance_object],
# which can be used to access the loaded entities and their __module__.
for modname, instance in output.items():
  print(modname, instance)
```

## JSON

[gyver.utils.json][] is a wrapper around orjson to make dumps return as string instead of bytes. Has a similar interface to most json libraries.

```python
from gyver.utils import json

val = json.loads('{"hello": "world"}')
val == json.dumps({"hello": "world"})
with open("myfile.json", "w") as stream:
  json.dump(val, stream)
with open("myfile.json") as stream:
  val = json.load(stream)
```

## Strings

[gyver.utils.strings][] has functions to parse some string formats.

- `def to_snake(camel_string: str) -> str`: changes any string to `snake_case`
- `def to_camel(snake_string: str) -> str`: changes any string to `camelCase`
- `def to_pascal(snake_string: str) -> str`: changes any string to `PascalCase`
- `def to_lower_kebab(anystring: str) -> str`: changes any string to `kebab-case`
- `def make_lex_separator(outer_cast: type[list | tuple | set], cast: type = str) -> Callable[[str], type[list | tuple | set]]`: makes a function that parses comma separated strings into the expected value with the shlex module

### Using lex separator
```python
from enum import Enum
from gyver.utils.strings import make_lex_separator

string1 = 'hello, world'
string2 = 'foo, bar, baz'
string3 = '1, 2, 3'

class MyEnum(Enum):
  FOO = 'foo'
  BAR = 'bar'
  BAZ = 'baz'

# here the parser will parse each item as a str
# and return them in a list
string1_parser = make_lex_separator(list, str)
string1_parsed = string1_parser(string1) # ["Hello", "world"]

# in the second case, the parser returns a set of enums
string2_parser = make_lex_separator(set, MyEnum)
string2_parsed = string2_parser(string2) # {MyEnum.FOO, MyEnum.BAR, MyEnum.BAZ}

# in the third case, the parser will return a tuple of ints
string3_parser = make_lex_separator(tuple, int)
string3_parsed = string3_parser(string3) # (1, 2, 3)
```

## Lazy

[gyver.utils.lazy][] has utilities to allow for lazily defined attributes so that you can avoid some patterns like the one below or avoid calculating a property twice.

```python
class MyClass:
  def __init__(self):
    self._val = None

  def get_val(self):
    if val is None:
      self._do_something()
    return self._val
```

### lazyfield



The [lazyfield][gyver.utils.lazyfield] descriptor streamlines the process of implementing lazy attributes. Here's how you can use it:

```python
from gyver.utils import lazyfield


class MyClass:
  @lazyfield
  def expensive_value(self):
    return do_expensive_operation()

instance = MyClass()
instance.expensive_value # Does the expensive operation, saves the result and returns the value
instance.expensive_value # Returns directly the cached value

del instance.expensive_value # Cleans the cache

instance.expensive_value # redo the expensive operation

instance.expensive_value = "Other" # Overwrites the cached value with the value assigned
```

!!! info
    `lazyfield` saves the value directly in the class as a hidden attribute so you don't have to worry about garbage collection or weakrefs
    

### asynclazyfield

The [asynclazyfield][gyver.utils.lazy] descriptor tackles the same issue as lazyfield, but while preserving the asynchronous API

```python
from gyver.utils import asynclazyfield

class MyClass:

  @asynclazyfield
  async def expensive_value(self):
    return await do_expensive_operation()

instance = MyClass()
await instance.expensive_value() # you still call it as a function, but it will do the same thing, call the function, store the result and return the value
await instance.expensive_value() # now it only returns the value

dellazy(instance, "expensive_value") # clear the stored value
await instance.expensive_value() # here the calculation is done again
setlazy(instance, "expensive_value", "Other") # overwrite the stored value with "Other"
```

!!! info
    the `asynclazyfield` does not support set and delete so there are helpers provided below to help with that

### Helpers

`gyver.utils.lazy` provides helpers to work with frozen classes or when using the asynclazyfield and need to set or reset the field manually

* `setlazy(instance: Any, attribute: str, value: Any, bypass_setattr: bool = False)` setlazy allows you to directly change the hidden attribute behind any lazy field, and the bypass_setattr parameter will instead of using the `setattr` function, use `object.__setattr__`.
* `dellazy(instance: Any, attribute: str, bypass_delattr: bool = False)` dellazy allows you to clear the value stored in the hidden attribute to allow for recalculation. Similar to setlazy the bypass_delattr parameter will use `object.__delattr__` instead of `delattr`
* `force_set(instance: Any, attribute: str, value: Any)` force_set is just a shortcut for setlazy(..., bypass_setattr=True)
* `force_del(instance: Any, attribute: str)` force_del is just a shortcut for dellazy(..., bypass_delattr=True)
* `is_initialized(instance: Any, attribute: str)`  Returns whether the lazyfield has stored a value yet, without triggering the routine inadvertently.
  
## Helpers

The [gyver.utils.helpers][] module provides several helper functions and classes that can assist you in various tasks. These helpers are designed to facilitate common operations and offer useful functionalities.

- [cache][gyver.utils.helpers] function is a wrapper around `functools.cache` but with improved type hints
- [deprecated][gyver.utils.helpers] decorator marks a function as deprecated and issues a warning when it's used. This is useful for indicating that a function is no longer recommended for use.
- [DeprecatedClass][gyver.utils.helpers] class is used to mark a class as deprecated. Instantiating this class will issue a deprecation warning. This is helpful when transitioning from old to new class structures.
- [merge_dicts][gyver.utils.helpers] function allows you to merge two dictionaries with customizable conflict resolution strategies. It's particularly useful when you need to combine dictionaries while handling potential conflicts.

## Timezone

The [gyver.utils.timezone][] module provides functions to work with timezones and date-time related operations.

- [now][gyver.utils.timezone] Get the current aware datetime.
- [today][gyver.utils.timezone] Get today's aware date.
- [make_now_factory][gyver.utils.timezone] Create a function to get the current aware datetime with a specific timezone.
