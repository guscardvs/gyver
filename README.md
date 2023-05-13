# Gyver

> Simple toolbox for python development to skip code boilerplate.

[**Documentation**](https://guscardvs.github.io/gyver/)

[**Source Code**](https://github.com/guscardvs/gyver)

## Authors

> [@guscardvs](https://github.com/guscardvs)

## Requirements

* Python 3.9+

## Required

* [OrJSON](https://github.com/ijl/orjson) for json parsing.
* [Pydantic](https://docs.pydantic.dev) for data handling.
* [Typing Extensions](https://github.com/python/typing_extensions) for compatibility.
* [Cryptography](https://cryptography.io) to handle encryption.

## Optional

To use the database parts:
* **Mysql/MariaDB:** AioMySQL, PyMySQL (use db-mysql or db-mariadb extras)
* **Postgres:** AsyncPG, Psycopg2
* **SQLite:** aiosqlite
* **Redis:** redis
* And **SQLAlchemy**

## Installation

```console
$ pip install gyver
```

## Roadmap

> Pack database code in a package specific "gyver-database" to make the gyver core lighter

##  License

This project is licensed under the terms of the MIT license.