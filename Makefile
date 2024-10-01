.PHONY: format test

format:
	@poetry run ruff format gyver tests
	@poetry run ruff check --fix gyver tests

test:
	@poetry run pytest
