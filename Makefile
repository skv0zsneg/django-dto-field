SHELL:=/usr/bin/env bash

.PHONY: unit
unit:
	uv run pytest

.PHONY: benchmark
benchmark:
	uv run python3 tests/e2e/manage.py benchmark

.PHONY: typing
typing:
	uv run mypy src

.PHONY: lint
lint:
	uv run ruff check --select I src
	uv run ruff format --check src
	uv run flake8 src --select=WPS

.PHONY: format
format:
	uv run ruff check --select I --fix src
	uv run ruff format src

.PHONY: test
test: unit

.PHONY: clean
clean: 
	rm -fr .mypy_cache .ruff_cache .pytest_cache htmlcov .coverage

.PHONY: all-checks
all-checks: clean lint typing test