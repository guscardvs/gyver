# Gyver


> _Simple toolbox for python development to skip code boilerplate._

---
 
**Documentation:** <a>Doclink</a>

**Source Code:** <a href="https://github.com/guscardvs/gyver" target="_blank">github.com/guscardvs/gyver</a>

---


## Requirements

Python 3.9+

### Required

* <a href="https://github.com/ijl/orjson" target="_blank">OrJSON</a> for json parsing.
* <a href="https://docs.pydantic.dev" target="_blank">Pydantic</a> for data handling.
* <a href="https://github.com/python/typing_extensions" target="_blank">Typing Extensions</a> for compatibility.
* <a href="https://github.com/guscardvs/context-handler" target="_blank">Context Handler</a> for client lifetime management.
* <a href="https://cryptography.io" target="_blank">Cryptography</a> to handle encryption.
  
### Optional

* To use the database parts:
  * Mysql/MariaDB: AsyncMy, PyMySQL (use db-mysql or db-mariadb extras)
  * Postgres: AsyncPG, Psycopg2
  * SQLite: aiosqlite
  * Redis: redis
  * And SQLAlchemy


## Installation

```console
$ pip install gyver

---> 100%
```

## Example

Add this to any python file

```python
from gyver.config import Config, ConfigLoader
from gyver.database import SyncDatabaseProvider, DatabaseConfig
import sqlalchemy as sa

# Creates a config instance to load environment variables
config = Config()

# loads all the DatabaseConfig attributes as environment
# variables, as such:
# DatabaseConfig.driver: DB_DRIVER
# DatabaseConfig.host: DB_HOST
# etc
db_config = ConfigLoader(config, prefix='db').load(DatabaseConfig)

# Creates a provider with the given configuration
# with an internal sqlalchemy engine setup
provider = SyncDatabaseProvider(db_config)

# opens a sqlalchemy connection
# connection using the context provided by
# the context-handler library
with provider.context().begin() as connection:
    # Do a hello world
    connection.execute(sa.select(sa.text('Hello World')))

```

This is one of the many features of **Gyver**

# License

This project is licensed under the terms of the MIT license.