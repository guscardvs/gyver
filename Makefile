.PHONY: format test

format:
	@poetry run black gyver tests
	@poetry run isort -ir gyver tests
	@poetry run autoflake --remove-all-unused-imports --remove-unused-variables --remove-duplicate-keys --expand-star-imports -ir gyver tests

test:
	@poetry run pytest
