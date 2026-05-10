# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

`pytest-hamilton` is a pytest plugin that creates automatic [Hamilton](https://github.com/apache/hamilton)-based fixtures for tests. The core plugin in `src/pytest_hamilton/pytest_hamilton.py` is fully implemented (option registration, dynamic fixture generation per DAG node, cleanup, three public fixtures: `hamilton_fixture_driver`, `hamilton_fixtures`, `input_config`).

## Tooling philosophy

- **`just` runs single-Python contributor verbs.** `qa`, `test`, `pdb`, `coverage` use `uv run` directly against `DEFAULT_PYTHON` (currently 3.14). Fast inner-loop feedback, no extra tool layer.
- **`nox` owns the matrix.** `just testall` and `just examples` shell out to `uvx nox`. Two sessions in `noxfile.py`:
  - `tests` — plugin's own test suite across Python 3.10–3.14.
  - `test_examples` — each `examples/exampleNN/` in its own venv, parametrized over (Python, example).
- **Examples are standalone copy-pasteable templates**, not in-repo subprojects. Each has its own `pyproject.toml` that declares `pytest-hamilton` from PyPI; a clearly-marked `[tool.uv.sources]` block redirects to the local checkout for dev only and is meant to be deleted on copy.

## Tooling

| Task | Command |
|------|---------|
| Format + lint + type-check + test (single Python) | `just qa` |
| Run tests, optional args (single Python) | `just test [ARGS]` |
| Run a single test | `just test tests/test_pytest_hamilton.py::test_name` |
| Drop into debugger on failure | `just pdb [ARGS]` |
| Coverage | `just coverage` |
| Plugin tests across all supported Pythons (via nox) | `just testall` |
| Each example template across all supported Pythons (via nox) | `just examples` |
| Run a single nox cell directly | `uvx nox -s "tests-3.13"` or `uvx nox -s "test_examples-3.12(example='example01')"` |

## Architecture

- `src/pytest_hamilton/` — package source (src layout)
  - `pytest_hamilton.py` — main plugin module
  - `cli.py` — Typer-based CLI entry point (`pytest_hamilton` command)
  - `utils.py` — utilities
- `tests/` — plugin tests (run by `just qa` / `just testall`)
- `examples/exampleNN/` — standalone project templates (run by `just examples`); each has its own pyproject and pytest config
- `noxfile.py` — matrix sessions; not invoked directly, only via `just testall` / `just examples`

## Linting and types

- **Ruff**: line length 120, rules E/W/F/I/B/UP enabled. `examples/` and `.nox/` are excluded — examples have their own pyproject and shouldn't be governed by the plugin's lint config.
- **ty**: Astral's type checker (all rules error by default).

## Publishing

GitHub Actions handles PyPI publishing (`.github/workflows/publish.yml`). Manual alternative: `just publish`.
