# SQLAlchemy Queries helper

Gyver provides query helpers to help with the following problems:

* you don't want your orm classes running all around your code
* you need a generic repository function to run selects, updates and deletes

## Example

Let's take as an example an generic function to run select on N fields on the following Person entity.

```python
from gyver.database import Entity
from gyver.database.sqlalchemy import SaContext
import sqlalchemy as sa

class Address(Entity):
    street = sa.Column(sa.Text)
    number = sa.Column(sa.Integer)
    country = sa.Column(sa.Text)
    zip_code = sa.Column(sa.Text)

class Person(Entity):
    name = sa.Column(sa.String(100))
    email = sa.Column(sa.Text)
    address_id = sa.Column(sa.Integer, sa.ForeignKey('address.id'))

    address = make_relation(Address, use_list=True)
```

Without gyver helpers the function would be something like:

```python

def list_people(context: SaContext, **comparison):
    # Note that it only supports equality comparison
    # and it doesn't support logical operations between comparisons
    # as well as any other problems
    q = sa.select(Person).where(
        *(
            getattr(Person, field, getattr(Address, field)) == value 
            for field, value in comparison.items()
        )
    )
    with context.begin() as connection:
        result = connection.execute(q)

# And then

list_people(context, name='anyname', zipcode="012345678")

```

With gyver you can do:

```python
from gyver.database import query

def list_people(context: SaContext, where: query.BindClause):
    q = sa.select(Person).where(where.bind(Person))
    with context.begin() as connection:
        result = connection.execute(q)

list_people(
    context, 
    query.and_(
        # here it access directly the name attribute on the person
        query.Where('name', 'anyname'), 
        # here it access the zipcode attribute on address and you have no chance
        # of conflict between names from Person and Address
        query.Where('address.zipcode', "012345678"),
        # you can also do different comparisons than equals
        query.Where('address.number', 3, query.comp.greater)
    )
)
```

## Clauses

Query helpers from gyver adhere to the Clause interface, either from:

* `BindClause`, or
* `ApplyClause`

### BindClause

BindClauses are clauses with the `.bind(mapper) -> query.Comparison` method, that expect a entity class, a table instance
or a ColumnCollection from sqlalchemy.
The comparison interface is for a sqlalchemy orm comparison or a boolean column

The BindClauses are:

* `query.Where(field: str, expected: T, comp: query.Comparator[T])`
* `query.and_(*where: query.BindClause)`
* `query.or_(*where: query.BindClause)`
* `query.AlwaysTrue()`
* `query.RawQuery(cmp: query.Comparison)`

### Apply Clause

ApplyClauses are clauses with the `.apply(query: sa.sql.Select) -> sa.sqlSelect` method, 
that expect a `Select` query instance and returns another.

The ApplyClauses are:

* `query.Paginate(limit: int, offset: int)`
* `query.OrderBy(field: typing.Optional[str], direction: OrderDirection)`
  
## Where

The `Where` class represents one comparison between a table and an expected value.
Its parameters are:

* `field: str`: the field on the entity
* `expected: T`: the expected value
* `comp: query.Comparator[T]`: a callable that can process the comparison between the field and the expected.

### Comparators

The `Comparator[T]` protocol is as follows:
```python

class Comparator(Protocol[T]):
    def __call__(self, field: ColumnElement | sa.Column, target: T) -> typing.Any:
        ...

# valid comparators

# the equals comparator can accept any datatype
def equals(field: ColumnElement | sa.Column, target: Any) -> Any:
    return field == target

class MyComparator:
    def __init__(self, parser):
        self.parser = parser

    # here MyComparator can only handle float values
    # this will be annotated on the Where class
    def __call__(field: ColumnElement | sa.Column, target: float) -> Any:
        return self.parser(field) == target
```

The `Where` class is dependent on a comparator and gyver ships with a lot of defaults:

* `always_true(field: FieldType, target: typing.Any)`: returns always a `sa.true()`
* `equals(field: FieldType, target: typing.Any)`: equivalent to `field == target`
* `not_equals(field: FieldType, target: typing.Any)`: equivalent to `field != target`
* `greater(field: FieldType, target: Sortable)`: equivalent to `field > target`
    * Sortable represents int, float, date, and time instances
* `greater_equals(field: FieldType, target: Sortable)`: equivalent to `field >= target`
* lesser(field: FieldType, target: Sortable): equivalent to `field < target`
* `lesser_equals(field: FieldType, target: Sortable)`: equivalent to `field <= target`
* `between(field: FieldType, target: tuple[Sortable, Sortable])` equivalent to `target[0] <= field <= target[1]`
* `range(field: FieldType, target: tuple[Sortable, Sortable])`: equivalent to `target[0] <= field < target[1]`
* `like(field: FieldType, target: str)`: equivalent to `FIELD LIKE '%{target}%'`
* `rlike(field: FieldType, target: str)`: equivalent to `FIELD LIKE '{target}%'`
* `llike(field: FieldType, target: str)`: equivalent to `FIELD LIKE '%{target}'`
* `insensitive_like(opt: typing.Literal["like", "rlike", "llike"] = "like")`: equivalent to the like options but as insensitive
    * `insensitive_like` returns a comparator so it must be called instead of passed as parameter. Eg.:
    ```python
    query.Where('field', expected, query.comp.insensitive_like('rlike'))
    ```
* `isnull(field: FieldType, target: bool)`: equivalent to `field is None if target else field is not None`
* `includes(field: FieldType, target: typing.Sequence)`: equivalent to `field in target`
* `excludes(field: FieldType, target: typing.Sequence)`: equivalent to `field not in target`
* `json_contains(field: FieldType, target: typing.Any)`: equivalent to `json_contains(field, '"target"')` (only mysql) (prefer normalizing table)
* `json_empty(field: FieldType, target: typing.Any)`: equivalent to `json_length(field) == 0 if target else json_length(field != 0`
* `make_relation_check(clause: BindClause)`: returns a relationship check (if exists) based on the clause.
    * Ex:
    ```python
    # This will do a query where
    query.Where(
        # if exists any address
        'address', 
        True, 
        # which
        make_relation_check(
            query.Where(
                # has an address number
                'address.number', 
                1, 
                # greater than 1
                query.comp.greater
            )
        )
    )
    ```
* `relation_exists(field: FieldType, target: bool)`: a relationship_check that checks only if exists

### Usage


* All people with the name starting with G
```python
query.Where('name', 'G', query.comp.rlike).bind(Person)
```
* People with the name ending with s that have a gmail
```python
query.and_(
    query.Where('name', 's', query.comp.llike),
    query.Where('email', 'gmail.com', query.comp.rlike)
).bind(Person)
```

* People with a given zipcode or with 'mayor' on the street name
```python
query.or_(
    query.Where('address.zipcode', '012345678'),
    query.Where('address.street', 'mayor', query.comp.insensitive_like())
).bind(Person)
```

* People with no address registered or people with any address registered from rule above
```python
query.or_(
    query.Where('address', False, query.comp.relation_exists),
    query.Where('address', True, query.comp.make_relation_check(
        query.or_(
            query.Where('address.zipcode', '012345678'),
            query.Where('address.street', 'mayor', query.comp.insensitive_like())
        )
    )
)
).bind(Person)
```

## Paginate

Paginate has a simple apply interface to paginate queries.
It has two implementations

* LimitOffsetPaginate: will do 
    ```python
    q.limit(self.limit).offset(self.offset)
    ```
* `make_field_paginate(field: str, jump_comparison: Comparator = query.comp.greater) -> FieldPaginate`: will do
    ```python
    q.where(query.Where(self.field, self.offset, self.jump_comparison)).limit(self.limit)
    ```

Both implementations have the same interface as Paginate.

### Usage

```python
    q = sa.select(Person)
    q = query.LimitOffsetPaginate(limit=10, offset=3).apply(q)

    # or
    FieldPaginate = make_field_paginate('id', query.comp.greater_equals)
    q = FieldPaginate(limit=10, offset=3).apply(q)
``` 

Paginate also have `IdPaginate` which is the result of `make_field_paginate('id')`

## OrderBy

Order by has a simple apply interface to order a query

```python
    q = sa.select(Person)

    q = query.OrderBy.asc('address.number').apply(q)

    # or
    
    q = query.OrderBy.desc('id').apply(q)

    # or

    q = query.OrderBy.none().apply(q) # do nothing
```

## Helpers

There are also some helper functions to wrap comparisons on some specific cases

* `query.as_date` will do date(field) == target
* `query.as_lower` will do lower(field) == target
* `query.as_time` will do time(field) == target
* `query.as_upper` will do upper(field) == target

### Usage

```python
query.Where('field', expected, query.as_date(query.comp.equals))
```
