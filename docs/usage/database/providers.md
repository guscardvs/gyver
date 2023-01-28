# Providers and Contexts

Gyver has two providers to work with the sqlalchemy interface
and both are powered by the same config class

## DatabaseConfig

`DatabaseConfig` inherits from ProviderConfig and has the following parameters:

* driver: `gyver.database.Driver`
    * `gyver.database.Driver` is an enum with the options:
        *  `.MYSQL`
        *  `.POSTGRES`
        *  `.SQLITE`
        *  `.MARIADB`
        *  `.CUSTOM`
* host: `str`
    * the host of the database, for **SQLite** databases use the filepath.
* port: `int`
    * the port of the database, if not passed, or passed -1 as value, will compute based on the default for the driver passed.
* user: `str`
    * the user to connect on the database. **Optional**
* password: `str`
    * the password to connect on the database. **Optional**
* name: `str`
    * the name to connect on the database. **Optional only if driver is SQLITE**
* pool_size: `int`
    * size of connection pool to be used, default is 20.
* pool_recycle: `int`
    * time in seconds to recycle a connection, default is 3600.
* max_overflow: `int`
    * max connections if the pool is empty, default is 0.

> To consult dialect default values use `database_config.dialect` and to consult the resolved port of the config use `database_config.real_port`.

> If you need another dialect implementation except the ones provider by Gyver,
> create a class that meets the protocol `gyver.database.drivers.interface.Dialect`,
> on the `.driver` of the config, pass `Driver.CUSTOM` and before you use the db_config
> call `db_config.override_dialect(YourDialect())`

### Usage

```python
from gyver.config import ConfigLoader
from gyver.database.config import DatabaseConfig

# in this case the expected environment variables will be
# DB_DRIVER (any of 'mysql', 'postgres', 'sqlite', 'mariadb', 'custom')
# DB_HOST database host without the schema
# DB_PORT port as integer (Optional)
# DB_USER database username (Optional) (Gyver will urlencode the username)
# DB_PASSWORD database password (Optional) (Gyver will urlencode the password)
# DB_NAME database name (Optional) (Gyver will urlencode the name)
# DB_POOL_SIZE pool size as integer (Optional)
# DB_POOL_RECYCLE pool recycle as integer (Optional)
# DB_MAX_OVERFLOW max overflow as integer (Optional)
config = ConfigLoader(prefix='db').load(DatabaseConfig)

# if you want to override the dialect implementation
# first check if sqlalchemy has support for the dialect
# then
class AioPGDialect:
    # port to be used if no port is passed on the config
    default_port = 5432
    # what driver match this dialect
    driver = Driver.POSTGRES
    # name of the dialect to sqlalchemy
    dialect_name = "postgresql"
    # async database driver implementation
    async_driver = "aiopg"
    # sync driver implemenation for sqlalchemy
    sync_driver = "psycopg2"
    # if should only use the host to construct the db
    # and ignore all the other config params
    only_host = False

# pass an instance of the dialect to the config
config.override_dialect(AioPGDialect())
```

## SyncDatabaseProvider

Synchronous implementation of the DatabaseProvider.
SyncDatabaseProvider will use the `.sync_driver` from the dialect.
If you don't pass a db_config as parameter, SyncDatabaseProvider instantiates one using
the 'db' as prefix to the configloader.
Has the following methods and attributes:

* `.config`: returns the db_config that was passed on instantiation
* `.is_closed(client: sqlalchemy.engine.Connection) -> bool`: returns if connection passed on parameter is closed
* `new() -> sqlalchemy.engine.Connection`: returns new sqlalchemy connection
* `release(client: sqlalchemy.engine.Connection) -> None`: close and release the connection
* `context(*, transaction_on: typing.Literal['open', 'begin'] | None = 'open') -> gyver.database.SaContext`: returns a context handler for a sqlalchemy connection. The transaction_on will begin a transaction either on an open call, a begin call, or never if none is passed.

`SaContext` has the following methods:

* `open() -> ContextManager[None]`: opens a connection, only if not opened yet in any higher frame, and yields None. If with transaction_on == 'open', opens a transaction(or a nested transaction if one is already open)
* `begin() -> ContextManager[sqlalchemy.engine.Connection]`: opens a connection, only if not opened yet in any higher frame, and yields the connetion instance. If with transaction_on == 'begin', opens a transaction(or a nested transaction if one is already open)
* `.client`: returns the connection or opens a new connection
* `transaction_begin(self) -> ContextManager[sqlalchemy.engine.Connection]`: runs `.begin` and opens a transaction(or a nested transaction if one is already open). Yields the connection
* `acquire_session(self) -> ContextManager[sqlalchemy.orm.Session]`: runs `.begin`, binds the connection to a Session and yields the session. If with transaction_on == 'begin', opens a transaction(or a nested transaction if one is already open)

### Usage

```python
from gyver.database import SyncDatabaseProvider
import sqlalchemy as sa

# instantiate the provider
# optionally you can pass a DatabaseConfig instance
provider = SyncDatabaseProvider()

# connection returned from provider.new is a valid sqlalchemy Connection
with provider.new() as connection:
    connection.execute(sa.select(sa.text('"Hello World"')))

def my_func(context):
    with context.begin() as connection:
        # here context.begin returns a valid sqlalchemy connection
        # if the context in which my_func is called has already called
        # context.begin or context.open
        # context.begin returns the same connection instantiated earlier
        connection.execute(sa.select(sa.text('"Hello World"')))

def my_other_func(context):
    with context.begin() as connection:
        connection.execute(sa.select(sa.text('"Hello World"')))

# create a context from this provider
context = provider.context()

with context.open():
    # using context.open() without passing anything to provider.context
    # will open a new transaction
    # the connections called from .begin inside this context manager will return the
    # same connection opened here
    my_func(context)
    my_other_func(context)
```

## AsyncDatabaseProvider

Asyncio implementation of the DatabaseProvider.
SyncDatabaseProvider will use the `.async_driver` from the dialect.
If you don't pass a db_config as parameter, AsyncDatabaseProvider instantiates one using
the 'db' as prefix to the configloader.
Has the following methods and attributes:

* `.config`: returns the db_config that was passed on instantiation
* `async def is_closed(client: sqlalchemy.engine.Connection) -> bool`: returns if connection passed on parameter is closed
* `async def new() -> sqlalchemy.engine.Connection`: returns new sqlalchemy connection
* `async def release(client: sqlalchemy.engine.Connection) -> None`: close and release the connection
* `def context(*, transaction_on: typing.Literal['open', 'begin'] | None = 'open') -> gyver.databaseAsyncSaContext`: returns a context handler for a sqlalchemy connection. The transaction_on will begin a transaction either on an open call, a begin call, or never if none is passed. AsyncSaContext `.begin` and `.open` are asynccontextmanagers


`AsyncSaContext` has the following methods:

* `open() -> AsyncContextManager[None]`: opens a connection, only if not opened yet in any higher frame, and yields None. If with transaction_on == 'open', opens a transaction(or a nested transaction if one is already open)
* `begin() -> AsyncContextManager[sqlalchemy.ext.asyncio.AsyncConnection]`: opens a connection, only if not opened yet in any higher frame, and yields the connetion instance. If with transaction_on == 'begin', opens a transaction(or a nested transaction if one is already open)
* `.client`: returns the connection or opens a new connection
* `transaction_begin(self) -> AsyncContextManager[sqlalchemy.ext.asyncio.AsyncConnection]`: runs `.begin` and opens a transaction(or a nested transaction if one is already open). Yields the connection
* `acquire_session(self) -> AsyncContextManager[sqlalchemy.ext.asyncio.AsyncSession]`: runs `.begin`, binds the connection to a Session and yields the session. If with transaction_on == 'begin', opens a transaction(or a nested transaction if one is already open)

### Usage

```python
from gyver.database import AsyncDatabaseProvider
import sqlalchemy as sa

# instantiate the provider
# optionally you can pass a DatabaseConfig instance
provider = AsyncDatabaseProvider()

# connection returned from provider.new is a valid sqlalchemy Connection
async with provider.new() as connection:
    await connection.execute(sa.select(sa.text('"Hello World"')))

async def my_func(context):
    async with context.begin() as connection:
        # here context.begin returns a valid sqlalchemy connection
        # if the context in which my_func is called has already called
        # context.begin or context.open
        # context.begin returns the same connection instantiated earlier
        await connection.execute(sa.select(sa.text('"Hello World"')))

async def my_other_func(context):
    async with context.begin() as connection:
        await connection.execute(sa.select(sa.text('"Hello World"')))

# create a context from this provider
context = provider.context()

async with context.open():
    # using context.open() without passing anything to provider.context
    # will open a new transaction
    # the connections called from .begin inside this context manager will return the
    # same connection opened here
    await my_func(context)
    await my_other_func(context)
```