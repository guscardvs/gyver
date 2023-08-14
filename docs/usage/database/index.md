# Working with Database

Gyver provides tools that streamline the process of working with databases, reducing the boilerplate required for database interactions.

## Example: Simplified Database Interaction

Here's an example that demonstrates how to use Gyver's database module to interact with a database using SQLAlchemy:

```python
from gyver.database import DatabaseAdapter, DatabaseConfig, Driver
import sqlalchemy as sa


# Create a DatabaseAdapter to load necessary configurations from the environment
# The DatabaseConfig class is annotated with `@as_config`, and DatabaseAdapter
# calls it using `AdapterConfigFactory().maker(DatabaseConfig, "db")`.
# Therefore, make sure your environment variables are prefixed with DB_<ATTRIBUTE>.
provider = DatabaseAdapter()
# Alternatively, you can configure the adapter manually
# If you set the port to -1 or leave it unset, the default port for the specified
# driver (in this case, 3306 for MySQL) will be used.
adapter = DatabaseAdapter(DatabaseConfig(
    driver=Driver.MYSQL,
    host="myhost",
    port=3306,
    user="myuser",
    password="mypassword"
    name="mydb",
    pool_size=10,
    pool_recycle=3600,
    max_overflow=0,
    autotransaction=False,
))

# Obtain the appropriate context for your desired SQLAlchemy component
context = adapter.context()        # for sqlalchemy's Connection
# context = adapter.session()       # for sqlalchemy's Session
# context = adapter.async_context() # for sqlalchemy's AsyncConnection
# context = adapter.async_session() # for sqlalchemy's AsyncSession

# Open a connection using the obtained context
with context as connection:
    # Run your SQLAlchemy code
    result = connection.execute(sa.select(sa.text("'Hello World'")))

# If you're using the asyncio interface
async with context as connection:
    result = await connection.execute(sa.select(sa.text("'Hello World'")))
```

The Gyver database module simplifies the process of establishing and managing database connections, enabling you to focus on writing database interactions without getting bogged down by intricate setup and teardown procedures. It's designed to enhance productivity and readability when working with databases in your Python projects.