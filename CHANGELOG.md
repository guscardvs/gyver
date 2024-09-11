## 5.0.2 (2024-09-11)

### Fix

- bump gyver-misc to allow any minor/patch

## 5.0.1 (2024-09-05)

### Fix

- bump gyver-misc to 0.4.0

## 5.0.0 (2024-07-29)

### Feat

- major changes, pydantic and tzdata are no longer required dependencies and using gyver-misc for miscellaneous instead of the .utils package

## 4.1.8 (2024-05-06)

### Fix

- added helpers to retrieve a dict[str, str] on gyver.url.query

## 4.1.7 (2024-04-24)

### Fix

- update gyver-attrs

## 4.1.6 (2024-04-24)

### Fix

- now config factory supports literal casting

## 4.1.5 (2024-04-20)

### Fix

- removed unused code

## 4.1.4 (2024-04-18)

### Fix

- **url**: updated url code to do a smarter faster copy without compromising API

## 4.1.3 (2024-03-28)

### Fix

- update email validator

## 4.1.2 (2024-03-28)

### Fix

- update vulnerable packages

## 4.1.1 (2024-03-04)

### Fix

- added from_args function to URL

## 4.1.0 (2024-03-04)

### Feat

- **config**: added config helpers

## 4.0.0 (2023-12-15)

### Feat

- removed database, cache and crypto modules and removed deprecated features

## 3.0.2 (2023-11-15)

### Fix

- updated libraries and imports

## 3.0.1 (2023-09-29)

### Fix

- updated interfaces for gyver/config to match code changes

## 3.0.0 (2023-09-29)

### Feat

- removed support for pydanticV2 to fix vulnerability

## 2.8.4 (2023-09-29)

### Fix

- updated pydantic to fix vulnerability

## 2.8.3 (2023-09-23)

### Fix

- updated cryptography version to remove vulnerability

## 2.8.2 (2023-09-15)

### Fix

- updated dependencies and added functions to properly handle with differences

## 2.8.1 (2023-09-15)

### Fix

- updated gyver-attrs to v0.7.0

## 2.8.0 (2023-09-01)

## 2.7.0 (2023-08-30)

## 2.6.1 (2023-08-14)

## 2.5.2 (2023-08-14)

## 2.5.1 (2023-08-11)

## 2.5.0 (2023-08-11)

### Feat

- added asynclazyfield and lazyfield helpers
- added support for env_cast in EnvConfig

### Fix

- added new method .from_netloc to url, added scheme as param to add and set and deprecated singleton module
- fixed some issues with typing and tests in the database module

## 2.3.4 (2023-07-14)

### Fix

- fixed bug in EnvConfig.get

## 2.3.3 (2023-07-05)

## 2.3.2 (2023-06-29)

### Fix

- changed typing for sqlalchemy comparison

## 2.3.1 (2023-06-29)

### Fix

- updated cchardet source to faust-cchardet

## 2.3.0 (2023-06-27)

## 2.2.0 (2023-06-20)

### Fix

- updated code to match new fix on gyver-attrs

## 2.0.8 (2023-03-15)

### Fix

- updated gyver-attrs to 0.4.0

## 2.0.7 (2023-03-11)

### Fix

- fixed sqlalchemy version

## 2.0.6 (2023-03-11)

### Fix

- updated project to use define instead of dataclasses or attrs

## 2.0.5 (2023-03-09)

### Fix

- updated gyver-attrs and deprecated singleton
- updated attrs version

## 2.0.3 (2023-03-07)

### Feat

- **database**: created applywhere to minimize boilerplate code while applying where objects and exported sessioncontext
- removed future module and deprecated old finder
- **pagination**: simplified interface
- **database**: simplified database interface

### Fix

- **config**: now does not require attrs to be installed
- removed asycmy and added sqlalchemy to db extras
- removed all # Compat marked features
- removed all deprecated features
- deprecated from_config
- removed boto tests and changed cryptoprovider to fernetcryptoprovider
- removed boto from gyver, working on simple-aws
- added value transformation to prevent resolver from passing list to cache features

## 1.3.1 (2023-02-12)

### Fix

- **config**: now tryeach only returns defaults if no name is found

## 1.3.0 (2023-02-12)

### Feat

- overall fixes and created "future" folder

### Fix

- removed unused singleton on crypto-provider
- **dialect**: added deprecated errors to old dialects and changed test to use new interface
- **database-dialects**: changed to a singular implementation and made aiomysql default to prevent bugs with sqlalchemy

### Refactor

- refactored atomic for a more concise name and implementation and revised finder

## 1.2.0 (2023-02-05)

### Feat

- **atomic-context**: improvements in atomic context and added boundcontext on atomic context

## 1.1.0 (2023-02-04)

### Feat

- **context**: implemenation of atomic context

## 1.0.0 (2023-02-01)

## 0.23.0 (2023-01-30)

### Feat

- **context**: added synchronization at context acquisition to prevent stack count bugs on concurrent environments

### Fix

- fixed actions to run only on more specific scenarios

## 0.22.0 (2023-01-28)

### Feat

- **context**: added thread/async safety to stack counter, improved documentation and added contextmanager interface

## 0.21.1 (2023-01-28)

### Fix

- **context-handler**: removed all mentions of context-handler

## 0.21.0 (2023-01-28)

### Feat

- **url/query**: added method chain to add and set on url, added encoding to slashes on query encode and added copy to url

### Fix

- **uri/query**: now unsafes slashes on quoting

## 0.20.1 (2023-01-27)

### Fix

- removed unused library context-handler

## 0.20.0 (2023-01-27)

### Feat

- **url**: created url module

## 0.19.3 (2023-01-25)

### Fix

- **query**: now uses field on cache

## 0.19.2 (2023-01-25)

### Feat

- **query**: added field resolver to make subqueries

## 0.19.1 (2023-01-24)

### Feat

- **context**: moved context code from context_handler to gyver

## 0.18.1 (2023-01-23)

### Fix

- **database**: fixed bug where syncdbprovider was creating an async uri

## 0.18.0 (2023-01-22)

### Feat

- small fixed and base mkdocs

## 0.17.0 (2023-01-21)

### Feat

- created configloader on provider config, added docs to finder and lazyfield, updated tests and changed defaults for style

## 0.16.0 (2023-01-19)

### Feat

- **database**: now default driver for mysql is asyncmy

## 0.15.2 (2023-01-19)

### Fix

- **query**: added maxlen to querycache

## 0.15.1 (2023-01-19)

### Fix

- **query**: fix bug where comparison is incorrectly evaluated at the if

## 0.15.0 (2023-01-19)

### Feat

- **query**: added cache to bind resolution

## 0.14.0 (2023-01-19)

### Feat

- **query**: added rawquery to database

## 0.13.3 (2023-01-12)

### Fix

- **database**: added clauses to handle pool_size

## 0.13.2 (2023-01-11)

### Fix

- **query**: now relationship orientation is evaluated based on the direction instead of the secondary table

## 0.13.1 (2023-01-10)

### Fix

- **query**: fixed typing on make_relation

## 0.13.0 (2023-01-09)

### Feat

- **query**: added support for existence validation on comparison

## 0.12.0 (2023-01-06)

### Feat

- **database**: added includes and excludes comp to query

## 0.11.1 (2023-01-06)

### Fix

- **query**: added support for querying if relationship exists

## 0.11.0 (2023-01-06)

### Feat

- **database**: added support for multilayer field querying

## 0.10.1 (2023-01-06)

### Fix

- **database**: fixed parameter mismatch on query

## 0.10.0 (2023-01-06)

### Feat

- **database**: added json comparators

## 0.9.0 (2022-12-28)

### Feat

- **boto-queue**: created sqs handler in gyver.boto.queue and changed credentials interface

## 0.8.0 (2022-12-28)

### Feat

- **cache**: created cache interface and added tests for cache storage and utils.singleton.make_singleton

## 0.7.0 (2022-12-13)

### Feat

- added cryptoprovider and utils.make_singleton

## 0.6.2 (2022-12-13)

### Fix

- **config**: now linesplit goes only once

## 0.6.1 (2022-12-12)

### Fix

- **model**: removed unnecessary print

## 0.6.0 (2022-12-12)

### Feat

- **database**: added custom database driver option

## 0.5.2 (2022-12-07)

### Fix

- **query**: fixed and tested new interface

## 0.5.1 (2022-12-07)

### Fix

- **query**: fixed interface conflict between where and bindclause

## 0.5.0 (2022-12-07)

### Feat

- **envconfig**: created envconfig feature

### Fix

- **query**: fixed interface conflict between where and bindclause

## 0.3.3 (2022-11-28)

### Fix

- **database**: fixed url generation

## 0.3.2 (2022-11-28)

### Fix

- **config**: fixed bug where prefix validation was inverse

## 0.3.1 (2022-11-28)

### Fix

- **database**: fixed make_table params

## 0.3.0 (2022-11-28)

### Feat

- **boto**: added storage provider feature to boto module
- added support for sanic and starlette apps and added finder and tests to it
- **tz**: added gyver.utils.timezone module
- **core**: created core features
