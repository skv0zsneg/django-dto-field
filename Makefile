SHELL:=/usr/bin/env bash

.PHONY: unit
unit:
	poetry run pytest

.PHONY: typing
typing:
	poetry run mypy src

.PHONY: lint
lint:
	poetry run ruff check --select I
	poetry run ruff format --check

.PHONY: format
format:
	poetry run ruff check --select I --fix
	poetry run ruff format

.PHONY: test
test: unit

.PHONY: all-checks
all-checks: lint typing unit