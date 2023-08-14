# Adapter and Contexts

Gyver provides a robust configuration class and adapter system that offers extensive support for various environments, facilitating seamless integration with different resources.

## DatabaseConfig

[DatabaseConfig][gyver.database] is decorated with [as_config][gyver.config] and encompasses the following configurable parameters:

* driver: [Driver][gyver.database], an enumeration with the options:
    *  `.MYSQL`
    *  `.POSTGRES`
    *  `.SQLITE`
    *  `.MARIADB`
    *  `.CUSTOM`
* host: `str`, The database host; for SQLite databases, provide the filepath.
* port: `int`, The database port; if not specified or set to -1, the default port for the chosen driver is used.
* user: `str`, The user for connecting to the database. (Optional)
* password: `str`, The password for connecting to the database. (Optional)
* name: `str`, The name for connecting to the database. (Optional, only for non-SQLite drivers)
* pool_size: `int`, the size of the connection pool to be used; the default is 20.
* pool_recycle: `int`, time in seconds before recycling a connection; the default is 3600.
* max_overflow: `int`, The maximum connections if the pool is full; the default is 0.

!!! note "Regarding Dialect Defaults and Customization"
    To check dialect default values, refer to the source code of [resolve_driver][gyver.database.drivers.utils]. To access the resolved port of the configuration, use database_config.effective_port.

    If you need a dialect implementation other than those provided by Gyver:
      - Ensure SQLAlchemy supports the dialect.
      - Create a class adhering to the [Dialect][gyver.database] protocol or create an instance of [DialectInfo][gyver.database] with the desired defaults..
      - Use `Driver.CUSTOM` in the `.driver` attribute of the configuration.
      - Prior to using `db_config`, call `db_config.override_dialect(your_dialect_instance)`.

### Usage

```python
from gyver.config import AdapterConfigFactory, DialectInfo
from gyver.database.config import DatabaseConfig

# In this case, the expected environment variables will include:
# DB_DRIVER (options: 'mysql', 'postgres', 'sqlite', 'mariadb', 'custom')
# DB_HOST (database host without the schema)
# DB_PORT (port as an integer) (Optional)
# DB_USER (database username) (Optional; Gyver will URL-encode the username)
# DB_PASSWORD (database password) (Optional; Gyver will URL-encode the password)
# DB_NAME (database name) (Optional; Gyver will URL-encode the name)
# DB_POOL_SIZE (pool size as an integer) (Optional)
# DB_POOL_RECYCLE (pool recycle as an integer) (Optional)
# DB_MAX_OVERFLOW (max overflow as an integer) (Optional)
config = AdapterConfigFactory().load(DatabaseConfig, __prefix__="db")

# To override the dialect implementation:
# 1. Verify if SQLAlchemy supports the desired dialect.
# 2. Create a class representing the dialect adhering to the Dialect protocol or create an instance of DialectInfo with the desired values.
# 3. Pass an instance of the dialect to the config.

class AioPGDialect:
    default_port = 5432
    driver = Driver.POSTGRES
    dialect_name = "postgresql"
    async_driver = "aiopg"
    sync_driver = "psycopg2"
    only_host = False

# Alternatively, create an instance of DialectInfo
aio_pg_dialect = DialectInfo(
    default_port=5432,
    driver=Driver.POSTGRES,
    dialect_name="postgresql",
    async_driver="aiopg",
    sync_driver="psycopg2",
    only_host=False,
)

config.override_dialect(AioPGDialect())
```

## The Adapter

Gyver provides an adapter for integration with SQLAlchemy, featuring a flexible interface already integrated with [gyver.context][].

!!! warning
    The Session context handler for both sync and asyncio interfaces internally employs an SQLAlchemy Connection, limiting session accessibility outside the context.

### Sync Interface

When working with a synchronous interface, you can utilize the adapter to perform various tasks.

Example:
```python
from gyver.database import DatabaseAdapter

# Create a new adapter instance
adapter = DatabaseAdapter()


# With the adapter at hand, you can create various 
# contexts for both the core and the
# ORM API of SQLAlchemy.
# adapter.context() returns a context handler 
# for the core API, utilizing 
# a sqlalchemy.engine.Connection as the resource.

adapter.context()

# adapter.session() returns a context handler 
# for the ORM API, utilizing a 
# sqlalchemy.orm.Session as the resource.

adapter.session()

# Should you need to directly use the 
# SQLAlchemy engine, access it 
# through adapter.engine.
adapter.engine
```

### The Asyncio Interface

When working with an asyncio driver, you can still use the same adapter with asyncio methods.

```python
from gyver.database import DatabaseAdapter

# Create a new adapter instance
adapter = DatabaseAdapter()

# With the adapter at hand, you can create 
# various contexts for both the
# core and the ORM API of SQLAlchemy.
# adapter.async_context() returns a 
# context handler for the core API, utilizing a 
# sqlalchemy.ext.asyncio.AsyncConnection as the resource.

adapter.async_context()

# adapter.async_session() returns a 
# context handler for the ORM API, utilizing a
# sqlalchemy.ext.asyncio.AsyncSession as the resource.
adapter.async_session()

# Should you need to directly use the 
# SQLAlchemy engine, access it through 
# adapter.async_engine.
adapter.async_engine
```

!!! warning
    By default, all database helper classes are frozen. To modify the configuration, create a new adapter instance.
