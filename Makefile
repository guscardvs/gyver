.PHONY: format test

format:
	@poetry run autoflake --remove-all-unused-imports --remove-unused-variables --remove-duplicate-keys --expand-star-imports -ir core tests
	@poetry run isort -ir core tests
	@poetry run black core tests

test:
	@poetry run pytest
