# Config

`Config` is the core feature to all `gyver` providers. It has helpers
to handle environment variables and create config classes in a declarative way. **Gyver prioritizes variables from the environment before environments read from files.**

!!! info "Package"
    
    All config features except the [AdapterConfigFactory][gyver.config] and [as_config][gyver.config]
    are isolated in the `env-star` package and can be installed as a standalone. However you will import using
    `from config import ...` instead of  `from gyver.config import ...`

## Config Class

The [Config][gyver.config] class is responsible for loading variables from the environment.

```python
from gyver.config import Config

config = Config()

# will search for MY_ENV_VAR on the environment
# or raise a `config.exceptions.MissingName` error
MY_ENV_VAR = config('MY_ENV_VAR')

# will search for CAST_ENV_VAR and try to pass as a parameter
# to int. on fail raises `config.exceptions.InvalidCast`
CAST_ENV_VAR = config('CAST_ENV_VAR', int)

# will search for DEFAULT_ENV_VAR and if not found will
# use 1 by default
DEFAULT_ENV_VAR = config('DEFAULT_ENV_VAR', int, default=1)
```

[Config][gyver.config] also accepts two params:

* `env_file: str | Path | None` which will import the dotenv file contents if the file exist. 
* mapping: [gyver.config.EnvMapping][] which uses to read the keys, by default uses a wrapper over `os.environ`

## EnvConfig

[EnvConfig][gyver.config] is a config subclass that uses an dotenv, depending on the value of the CONFIG_ENV in the environment. It uses a env enum and applies a weight to each possible value:

* [Env][gyver.config].([PRD][gyver.config.Env] > [DEV][gyver.config.Env] > [TEST][gyver.config.Env] > [LOCAL][gyver.config.Env] )
  
These values are read from the environment as lowercase.

```python
from gyver.config import EnvConfig, Env, DotFile

# Here EnvConfig accepts may read one of two env files
# depending on the CONFIG_ENV value.
# If CONFIG_ENV=prd, loads the .env file
# If CONFIG_ENV=dev or lower, loads the .env-dev file
config = EnvConfig(
    Dotfile('.env-dev', Env.DEV, apply_to_lower=True), 
    DotFile('.env', Env.PRD)
)

MY_ENV_VAR = config('MY_ENV_VAR')
```

For more information on EnvConfig's attributes check the [API Reference](../reference/config.md#gyver.config.EnvConfig)

## Grouping variables in classes


[gyver.config][] is also tuned to load classes as configuration by introspecting into
their fields. In this way you can use classes to group environment variables together
and add custom prefixes and defaults to it.

!!! info

    Currently it will support any class defined by:
        
        - Pydantic V1
        - attr.s
        - dataclasses
        - gyver-attrs
    But it is more properly prepared to deal with the helper gyver-attrs method
    [as_config][gyver.config]

```python
from gyver.config import Config, AdapterConfigFactory, as_config


# Create a class decorated by as_config (or create a dataclass, a pydantic model or an attrs.define class)
@as_config
class MyProviderConfig:
    # the dunder prefix attribute will be used to 
    # make the names to the environment variables
    # for example: with the name attribute
    # AdapterConfigFactory will lookup for SERVICE_NAME in config
    # By default is an empty string
    __prefix__ = 'service'
    
    # the without prefix dunder attribute will be used
    # to avoid prefixing to the attributes passed
    __without_prefix__ = (
        'max_connections', 
        'connection_recycle'
    )

    # the type here will be used as cast in the call function
    name: str
    max_connections: int = 10
    connection_recycle: int = 3600

config = Config() # or EnvConfig

# AdapterConfigFactory starts with a config instance, or if none, it will use a default
# Config()
factory = AdapterConfigFactory(config)

# here the factory will do:
# MyProviderConfig(
#   name=config('SERVICE_NAME', str),
#   max_connections=config('MAX_CONNECTIONS', int, 10)
#   connection_recycle=config('CONNECTION_RECYCLE', int, 3600)
# )
# AdapterConfigFactory will retry with lowercase as well before raising
# `config.exceptions.MissingName`
my_provider_config = config_loader.load(MyProviderConfig)

# here is essentially the same as
# my_provider_factory = lambda: config_loader.load(MyProviderConfig)
my_provider_factory = config_loader.maker(MyProviderConfig)
```

[load][gyver.config.AdapterConfigFactory] also accepts presets as keyword arguments.
The keyword arguments passed to `.load` will not be searched in the config.

`AdapterConfigFactory` also has the function `.resolve_confignames(cls, root: Path) -> dict` which uses finder to lookup at `root` and returns all possible environment variables based on the marked configuration classes, if you are not using as_config but still want this to find your configuration class, decorate the class with [mark][gyver.config].
## Marking Classes as Config


Use the [mark][gyver.config] function to mark a class as a config class. When a class is marked using this function, it helps improve the accuracy of identifying classes intended for use as config classes. This is particularly useful when using the resolve_confignames function to determine the environment variables that a class expects.

!!! note
    Note that even if not marked as a config class, [load][gyver.config.AdapterConfigFactory] will still process the class attributes correctly, however [resolve_confignames][gyver.config.AdapterConfigFactory] will not be able to find this class and show it.

```python
from gyver.config import mark
from pydantic import BaseModel

@mark
class MyConfigClass(BaseModel):
    # Class fields...

# Use resolve_confignames to 
# find environment variables 
# associated with marked config classes
config_variables = AdapterConfigFactory.resolve_confignames(Path('/path/to/project'))

# This will only include classes 
# marked using the mark function
# Avoiding false positives and 
# providing accurate results
```
## Helpers

[gyver.config] comes with various helpers for some common cases.

- [boolean_cast][gyver.config] can be used instead of passing bool directly and only validating if the value is truthy.
    Example:
    ```python
    # TRUE_ENV_VAR=1
    # FALSE_ENV_VAR=False
    from gyver.config import Config, boolean_cast

    config = Config()

    # Here the value returned is True, 
    # but not because it is reading properly the value
    # instead because the value is not empty
    config("TRUE_ENV_VAR", bool)

    # Now boolean_cast is effectly evaluating if the value exists and 
    # if the value.lower() in (1, "true")
    config("TRUE_ENV_VAR", boolean_cast)

    # Here it will wrongly return the value as True
    # because it is only evaluating if the value is not empty
    config("FALSE_ENV_VAR", bool)

    # Here it will return false because it is evaluating
    # value.lower() in (0, "false", "")
    config("FALSE_ENV_VAR", boolean_cast)
    ```
- [valid_path][gyver.config] is a utility function that converts a string to a Path object and checks if the path exists.
    Example:
    ```python
    #PATH_ENV=/path/to/existing/file.txt
    from gyver.config import valid_path, Config

    config = Config()

    # Here config properly evaluates the path and checks
    # if it .exists() or raises an Exception if it does not.
    config("PATH_ENV", valid_path)

    ```
- [joined_cast][gyver.config] is a helper function that enables joined casting.
    Example:
    ```python
    # SHOULD_BE_INT=1.034
    from gyver.config import Config, joined_cast

    config = Config()

    # here joined cast will receive 1.034 string, 
    # then cast it to float and then cast it to int
    # providing the expected value with n transformations
    config("SHOULD_BE_INT", joined_cast(float).cast(int))
    ```

- [with_rule][gyver.config] is a helper function that applies a rule check to a value and raises an InvalidEnv exception if the rule is not satisfied.
    Example:
    ```python
        # DB_MAX_CONNECTIONS=-3
        from gyver.config import with_rule, Config, joined_cast
        
        config = Config()

        def should_be_positive(value: int):
            return value > 0
        
        # Here with rule will raise an exception, because
        # DB_MAX_CONNECTIONS does not pass the rule expected `should_be_positive`
        config("DB_MAX_CONNECTIONS", joined_cast(int).cast(with_rule(should_be_positive)))

        # However you can quickly fix that just by joining another function
        # now the rule does not raise errors and the value returns correctly
        config("DB_MAX_CONNECTIONS", joined_cast(int).cast(lambda val: min(1, val)).cast(with_rule(should_be_positive)))
    ```