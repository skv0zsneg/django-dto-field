SHELL:=/usr/bin/env bash

.PHONY: db-up
db-up:
	docker compose up -d

.PHONY: db-down
db-down:
	docker compose down -v

.PHONY: unit
unit:
	poetry run pytest

.PHONY: benchmark
benchmark:
	poetry run python3 benchmarks/jsonfield_benchmark.py

.PHONY: typing
typing:
	poetry run mypy src

.PHONY: lint
lint:
	poetry run ruff check --select I src
	poetry run ruff format --check src

.PHONY: format
format:
	poetry run ruff check --select I --fix src
	poetry run ruff format src

.PHONY: test
test: unit

.PHONY: all-checks
all-checks: lint typing test