# SQLAlchemy Defaults

Gyver has some defaults to help speedup development with sqlalchemy

* `gyver.database.default_metadata: sqlalchemy.MetaData`: default metadata object to be used in gyver defaults
* gyver has entities defaults and table factories

## Entities

Gyver calls entities the orm models that describe the database.
By default gyver has 2 abstract classes:

* `gyver.database.AbstractEntity`: abstract entity is the declarative base and implements the default tablename as the classname in lowercase
* `gyver.database.Entity(AbstractEntity)`: entity inherits from abstract entity (it is abstract as well) and implements an id column as integer primary_key that can be accessed by `.id_` or `.pk`

## Table Factories

Gyver has 2 table factories:

* `make_table(name: str, *args, **kwargs) -> sa.Table`: wrapper around sa.Table creation that binds to the `gyver.database.default_metadata`
* `create_relation_table(table_name: str, *entities: str) -> sa.Table`: helper to create relation tables on m2m relationships. The table_name is the name to be used in the relation table, and the entities are the names of the tables related. will produce a result table with an integer pk, and will create a column as such: 
> `sa.Column(f"{entity}_id", sa.Integer, sa.ForeignKey(f"{entity}.id"))`

## Relation Helper

Gyver also has a helper function to improve typing with sqlalchemy in the `sqlalchemy.orm.relationship` factory.

```python
gyver.database.utils.make_relation(
    relation: typing.Union[
        str, type[EntityT], typing.Callable[[], type[EntityT]]
    ],
    *,
    relation_name: str = "",
    back_populates: typing.Optional[str] = None,
    secondary: typing.Union[sa.Table, type, None] = None,
    foreign_keys: typing.Optional[list[typing.Any]] = None,
    lazy: str = "selectin",
    use_list: bool = False,
)
```

* `relation`: can be the str name of the class, the class type or a function that returns the class.
    * if relation is `str`, make_relation will assume the return type is `Any`
    * if relation is the `class`, make_relation will assume the return type is a instance of that class
    * if relation is the `function` `make_relation` will assume the return type is an instance of the class returned by the function. This can be used to resolve circular import issues as make_relation will not call this function ever.
        * if you pass the `function`, the `relation_name` is mandatory and requires the name of the class as `string`
* `relation_name`: a string of the name of the class. will only be used if the relation attribute receies a function.
* `back_populates`, `foreign_keys` and `lazy` will be used directly to the `sqlalchemy.orm.relationship`
* `use_list`: is not used, but annotates to the function that the expected return should be a list.
  

## Alembic and migrations

To integrate with alembic, add this to your `env.py`:

```python
from myproject import db_config, ROOT_DIR
from gyver.database import make_uri, default_metadata, AbstractEntity
from gyver.utils import Finder, instance_finder, class_finder
import sqlalchemy as sa

# alembic code ...
# use the default metadata from gyver
target_metadata = default_metadata

# create finders to import all the tables and classes used in your project, so that
# you don't need to be importing them one by one
finders = [
    Finder(instance_finder(sa.Table),ROOT_DIR), 
    Finder(class_validator(AbstractEntity), ROOT_DIR)
]
for finder in finders:
    # Run the finders
    finder.find()


# create the uri using the config and the sync mode
# alembic does not support asyncio drivers
target_db_uri = make_uri(db_config, sync=True)

# alembic code ...

def run_migrations_offline() -> None:
    # use the created uri to run the migrations
    context.configure(
        url=target_db_uri,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # use the same uri as on run_migrations offline
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

# alembic code ...

```