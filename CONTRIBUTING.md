# Contributing to `django-dto-field`

Thank you for your interest in contributing! This document provides guidelines and instructions to help you get started.

## Project Overview

`django-dto-field` provides an easy-to-use, production-ready Django Model Field for storing DTO (Data Transfer Object) data with blazing-fast serialization/deserialization. 

**Core Tech Stack:**
*   **Python:** 3.10 - 3.14
*   **Framework:** Django >= 4.2.0
*   **Serialization:** `msgspec` (for high-performance encoding/decoding)
*   **Build & Package Management:** `uv`

## Getting Started

We use `uv` for dependency management and virtual environments.

1.  **Install `uv`** (if you haven't already):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
2.  **Install dependencies:**
    ```bash
    uv sync
    ```
    *(Note: `uv sync` automatically installs all dev dependencies and sets up the virtual environment based on `uv.lock`).*

## Code Quality & Standards

We maintain strict code quality standards. CI will fail if any of the following are not met:

### 1. 100% Test Coverage
We require **100% code coverage** for all new and existing code. 
*   Tests are written using `pytest` and `pytest-django`.
*   Coverage is enforced via `pytest-cov`.
*   If you add a new feature or fix a bug, you **must** write tests for it. Run with `make test`.

### 2. Strict Typing
*   We use `mypy` with `django-stubs` for static type checking.
*   All public APIs and complex internal logic must be fully typed.
*   Run `make typing` to verify your types before committing.

### 3. Linting and Formatting
We use a hybrid approach for linting to ensure both modern formatting and strict architectural rules:
*   **Ruff:** Used for blazing-fast code formatting and import sorting (`isort`).
*   **Flake8 + Wemake Python Styleguide (WPS):** Used for strict logic, complexity, and architectural linting. *Note: WPS is highly opinionated and strict. Please review their documentation if you encounter unfamiliar errors.*

Run `make format` to automatically fix formatting and import issues.

## Development Commands

We use a `Makefile` to standardize development workflows. All commands automatically run inside the `uv` virtual environment.

| Command | Description |
| :--- | :--- |
| `make test` | Run the full unit test suite with coverage (alias for `make unit`). |
| `make typing` | Run `mypy` type checks on the `src` directory. |
| `make lint` | Run `ruff` (imports) and `flake8` (WPS rules) checks. |
| `make format` | Auto-fix imports (`ruff`) and format code (`ruff format`). |
| `make all-checks` | Clean caches and run linting, typing, and tests (Recommended before PR). |

## Submitting a Pull Request

Before opening a PR, please ensure:
1.  Your code passes `make all-checks` locally.
2.  Test coverage remains at 100%.
3.  Commit messages are clear and follow conventional commits (optional but appreciated).
4.  You have updated the documentation/docstrings if you changed public APIs.

Thank you for helping make `django-dto-field` better!