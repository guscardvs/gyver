# Gyver

> Simple toolbox for python development to skip code boilerplate.

[**Documentation**](https://guscardvs.github.io/gyver/)

[**Source Code**](https://github.com/guscardvs/gyver)

This documentation refers to version **2.5.1**

## Authors

> [@guscardvs](https://github.com/guscardvs)

## Requirements

* Python 3.9+


## Required

* [OrJSON](https://github.com/ijl/orjson) for json parsing.
* [Pydantic 1.x](https://docs.pydantic.dev) for data handling. (Support for v2 is under development)
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

<!-- termynal -->

```
$ pip install gyver
---> 100%
Done!
```

## Roadmap

> Move database related code to a separate library and add support for Pydantic V2

##  License

This project is licensed under the terms of the MIT license.