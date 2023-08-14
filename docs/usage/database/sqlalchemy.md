# SQLAlchemy Defaults

Gyver offers default settings designed to expedite development with SQLAlchemy. These defaults include:

- gyver.database.default_metadata: A pre-configured sqlalchemy.MetaData object intended for use with Gyver defaults.
- Gyver's default entities and table factories

## Entities

In Gyver, entities refer to the ORM models that define your database structure. By default, Gyver provides two abstract classes:

* [AbstractEntity][gyver.database]: This abstract entity serves as the declarative base and automatically assigns the class name in lowercase as the default table name.
* [Entity][gyver.database]: Building on the abstract entity, the Entity class (also abstract) includes an integer primary key column named id that can be accessed through `.id_` or `.pk`.

## Table Factories

Gyver introduces two table factories to simplify your work:

* [make_table][gyver.database]: A wrapper around sa.Table creation, it is bound to the gyver.database.default_metadata. This offers streamlined table creation.
* [create_relation_table][gyver.database]: This helper aids in generating relation tables for many-to-many relationships. You can define the table name and related entities. The resulting table will have an integer primary key column and foreign key columns linking to the respective entities.


## Alembic and migrations

For seamless integration with Alembic, follow these steps in your `env.py`:

```python
from myproject import db_config, ROOT_DIR
from gyver.database import make_uri, default_metadata, AbstractEntity
from gyver.utils import FinderBuilder
import sqlalchemy as sa

# ... Alembic code ...

# Utilize the default metadata from Gyver
target_metadata = default_metadata

# Create finders to import all used tables and classes
# This eliminates the need for individual imports
FinderBuilder().instance_of(sa.Table).child_of(AbstractEntity).from_path(ROOT_DIR).find()


# Create the URI using the configuration and sync mode
# Alembic does not support asyncio drivers
target_db_uri = make_uri(db_config, sync=True)

# ... Alembic code ...

def run_migrations_offline() -> None:
    # Use the created URI to run migrations
    context.configure(
        url=target_db_uri,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


    # Use the same URI as in the run_migrations_offline
    cfg = config.get_section(config.config_ini_section)
    cfg["sqlalchemy.url"] = target_db_uri  # type: ignore
    connectable = engine_from_config(
        cfg,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# ... Alembic code ...

```