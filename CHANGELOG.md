## 2.0.0 (2023-02-24)

### Feat

- removed future module and deprecated old finder
- **pagination**: simplified interface
- **database**: simplified database interface

### Fix

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

## 0.2.0 (2022-11-09)

### Feat

- **tz**: added gyver.utils.timezone module
- **core**: created core features
