# Config

`Config` is the core feature to all `gyver` providers. It has helpers
to handle environment variables and create config classes in a declarative way. **Gyver prioritizes variables from the environment before environments read from files.**

## Config Class

The `Config` class is responsible for loading variables from the environment.

```python
from gyver.config import Config

config = Config()

# will search for MY_ENV_VAR on the environment
# or raise a `gyver.exc.MissingName` error
MY_ENV_VAR = config('MY_ENV_VAR')

# will search for CAST_ENV_VAR and try to pass as a parameter
# to int. on fail raises `gyver.exc.InvalidCast`
CAST_ENV_VAR = config('CAST_ENV_VAR', int)

# will search for DEFAULT_ENV_VAR and if not found will
# use 1 by default
DEFAULT_ENV_VAR = config('DEFAULT_ENV_VAR', int, default=1)
```

`Config` also accepts two params:

* `env_file: str | Path | None` which will import the dotenv file contents if the file exist. 
* mapping: `gyver.config.EnvMapping` which uses to read the keys, by default uses a wrapper over `os.environ`

## EnvConfig

`EnvConfig` is a config subclass that uses an dotenv, depending on the value of the CONFIG_ENV in the environment. It uses a env enum and applies a weight to each possible value:

* `Env.`(`PRD` > `DEV` > `TEST` > `LOCAL` )
  
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

`EnvConfig` also accepts a parameter `env_var` which will look for the CONFIG_ENV value. By default uses `CONFIG_ENV`.

## ProviderConfig

`ProviderConfig` inherits from `gyver.model.Model` and integrates with the config module, importing the attributes of the class from the environment.

```python
from gyver.config import Config, ConfigLoader, ProviderConfig

# Create a class inheriting from ProviderConfig
class MyProviderConfig(ProviderConfig):
    # the dunder prefix attribute will be used to 
    # make the names to the environment variables
    # for example: with the name attribute
    # ConfigLoader will lookup for SERVICE_NAME in config
    __prefix__ = 'service'
    
    # the without prefix dunder attribute will be used
    # to avoid adding the prefix to the attributes passed
    __without_prefix__ = (
        'max_connections', 
        'connection_recycle'
    )

    name: str
    max_connections: int = 10
    connection_recycle: int = 3600

config = Config() # or EnvConfig

# ConfigLoader starts with a config instance
# and also accepts prefix and without_prefix as params.
# prefix and without_prefix from ConfigLoader
# are always used if passed instead of the passed on the class
config_loader = ConfigLoader(config)

# here the config_loader will do:
# MyProviderConfig(
#   name=config('SERVICE_NAME', str),
#   max_connections=config('MAX_CONNECTIONS', int, 10)
#   connection_recycle=config('CONNECTION_RECYCLE', int, 3600)
# )
# ConfigLoader will retry with lowercase as well before raising
# `gyver.exc.MissingName`
my_provider_config = config_loader.load(MyProviderConfig)
    
```

`ConfigLoader.load` also accepts presets as keyword arguments.
The arguments passed to `.load` will not be searched in the config.

`ConfigLoader` also has the function `.resolve_confignames(cls, root: Path) -> dict` which uses finder to lookup at `root` and returns a dict with the key as the found ProviderConfig subclass and its values are a sequence of tuples containg all the attribute names that will be used on the config.