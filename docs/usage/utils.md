# Utils
Utils is a module with a lot of functions and classes for diverse use cases and does not depend on any libraries or gyver features.

## Exceptions

`gyver.utils.exc` has a single function:

* `def panic(exc: type[ExceptionT], message: str) -> ExceptionT`:
   `panic` instantiates the `exc` class with `message` as its first parameter with an exclamation mark appended to it. If `message` already endswith an exclamation mark, panic will overwrite it.

```python
from gyver.utils import panic

# raises IndexError with first arg as "Index should be 1!"
raise panic(IndexError, "Index should be 1")
```


## Finder

`gyver.utils.finder` provides an interface to search for and import specific entities (defined by a user-provided validator function) from a codebase.
This can be useful if you need to load dinamically entities into the namespace, for example, in a migration script.

By default gyver ships with two validators:

- `instance_validator(*types: type)` which using with finder, selects entities that are instances of any of the `types` provided.

- `class_validator(*types: type)` which using with finder, selects entities that inherit from any of the `types` provided. `class_validator` excludes the parent class for the match.

```python
from gyver.utils import Finder, instance_validator
from pathlib import Path

MY_ROOT_DIR = Path(__file__).parent

class MyClass:
  def __init__(self):
    self.value = 1

# Create an Finder instance using instance_validator passing
# your desired class(es) as its parameter and the root dir.
# Your root dir will be used to import. Ex: my_root_dir.mymod.myclass_instance
finder = Finder(instance_validator(MyClass), MY_ROOT_DIR)

# Run finder.find() to search for the instances
# After this step your instances are already loaded on the namespace
finder.find()

# if you actually need to handle the output
# the output mapping is [modname: str, instance: instance_object]
# which can be used to access the loaded entities and their __module__
for modname, instance in finder.output.items():
  print(modname, instance)

```

## JSON

`gyver.utils.json` is a wrapper around orjson to make dumps return as string instead of bytes. Has a similar interface to most json libraries.

```python
from gyver.utils import json

val = json.loads('{"hello": "world"}')
val == json.dumps({"hello": "world"})
```

## Strings

`gyver.utils.strings` has functions to parse some string formats.

- `def to_snake(camel_string: str) -> str`: changes camelCase to snake_case
- `def to_camel(snake_string: str) -> str`: changes snake_case to camelCase
- `def upper_camel(snake_string: str) -> str`: changes snake_case to UpperCamelCase
- `def make_lex_separator(outer_cast: type[list | tuple | set], cast: type = str) -> Callable[[str], type[list | tuple | set]]`: makes a function that parses comma separated strings into the expected value

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
string1_parsed = string1_parser(string1)

# in the second case, the parser returns a set of enums
string2_parser = make_lex_separator(set, MyEnum)
string2_parsed = string2_parser(string2)

# in the third case, the parser will return a tuple of ints
string3_parser = make_lex_separator(tuple, int)
string3_parsed = string3_parser(string3)
```
