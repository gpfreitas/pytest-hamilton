# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

`pytest-hamilton` is a pytest plugin that creates automatic [Hamilton](https://github.com/apache/hamilton)-based fixtures for tests. The project is in early development — the core plugin logic in `src/pytest_hamilton/pytest_hamilton.py` is a stub.

## Tooling

The project uses `uv` for dependency management and `just` as a task runner.

| Task | Command |
|------|---------|
| Format + lint + type-check + test | `just qa` |
| Run tests (with optional args) | `just test [ARGS]` |
| Run a single test | `just test tests/test_pytest_hamilton.py::test_name` |
| Drop into debugger on failure | `just pdb [ARGS]` |
| Type check | `uv run --python=3.13 --extra test ty check .` |
| Lint | `uv run --python=3.13 --extra test ruff check .` |
| Format | `uv run --python=3.13 --extra test ruff format .` |
| Coverage | `just coverage` |
| Test across all supported Python versions (3.10–3.13) | `just testall` |

## Architecture

- `src/pytest_hamilton/` — package source (src layout)
  - `pytest_hamilton.py` — main plugin module (stub, to be implemented)
  - `cli.py` — Typer-based CLI entry point (`pytest_hamilton` command)
  - `utils.py` — utilities
- `tests/` — pytest tests

## Linting and types

- **Ruff**: line length 120, rules E/W/F/I/B/UP enabled
- **ty**: Astral's type checker (all rules error by default)

## Publishing

GitHub Actions handles PyPI publishing (`.github/workflows/publish.yml`). Manual alternative: `just publish`.
