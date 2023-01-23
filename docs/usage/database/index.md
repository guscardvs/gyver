# Working with Database

Gyver ships some tools to reduce boilerplate when running with the database

## Example

```python
from gyver.database import SyncDatabaseProvider
import sqlalchemy as sa


# create a SyncProvider which will load the
# necessary configs from the environment
# SyncProvider wraps an sqlalchemy Engine
provider = SyncDatabaseProvider()

# create a context and begin the connection
with provider.context().begin() as connection:
    # run your sqlalchemy code
    result = connection.execute(sa.select(sa.text("'Hello World'")))

# or

# create an AsyncProvider
# AsyncProvider wraps an sqlalchemy AsyncEngine
provider = AsyncDatabaseProvider(db_config)

# create a context and begin the connection
async with provider.context().begin() as connection:
    # run your sqlalchemy code
    result = await connection.execute(sa.select(sa.text("'Hello World'")))
```