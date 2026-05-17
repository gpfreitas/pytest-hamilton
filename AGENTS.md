# AGENTS.md

This file provides guidance to coding agents working in this repository.

## Project overview

`pytest-hamilton` is a pytest plugin that creates automatic [Hamilton](https://github.com/apache/hamilton)-based fixtures for tests. The core plugin in `src/pytest_hamilton/pytest_hamilton.py` is fully implemented (option registration, dynamic fixture generation per DAG node, cleanup, three public fixtures: `hamilton_fixture_driver`, `hamilton_fixtures`, `input_config`).

## Tooling philosophy

- **`just` runs single-Python contributor verbs.** `qa`, `test`, `pdb`, `coverage` use `uv run` directly against `DEFAULT_PYTHON` (currently 3.14). Fast inner-loop feedback, no extra tool layer.
- **`nox` owns the matrix.** `just testall` and `just examples` shell out to `uvx nox` — `nox` is intentionally not a project dep, so it runs in its own ephemeral environment and does not pollute the project venv. Two sessions in `noxfile.py`:
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
| Build the wheel + sdist | `just build` |
| Build the conda package locally (requires `rattler-build` on PATH) | `just conda-build` |

## Architecture

- `src/pytest_hamilton/` — package source (src layout)
  - `pytest_hamilton.py` — the plugin (single module; no CLI, no helpers)
- `tests/` — plugin tests (run by `just qa` / `just testall`)
- `examples/exampleNN/` — standalone project templates (run by `just examples`); each has its own pyproject and pytest config
- `noxfile.py` — matrix sessions; not invoked directly, only via `just testall` / `just examples`

### Plugin lifecycle

- `pytest_addoption` — registers CLI flags (`--hamilton-modules`, `--hamilton-config`) and their `ini` counterparts.
- `pytest_configure` — scans the configured Hamilton modules, builds a `hamilton.driver.Driver`, and dynamically attaches one fixture function per DAG node to the `pytest_hamilton.pytest_hamilton` module.
- `pytest_unconfigure` — removes the dynamic fixtures and reverses any `sys.path` mutations.

## Linting and types

- **Ruff**: line length 120, rules E/W/F/I/B/UP enabled. `examples/` and `.nox/` are excluded — examples have their own pyproject and shouldn't be governed by the plugin's lint config.
- **ty**: Astral's type checker (all rules error by default).

## Testing notes

- Tests use the `pytester` fixture with `runpytest_subprocess`, which runs pytest in a child process so plugin loading and configuration are verified end-to-end.
- **Coverage caveat:** `runpytest_subprocess` bypasses standard coverage collection, so the headline coverage number (~36%) understates what is actually exercised. Don't chase it as a real gap without first reproducing in-process.

## Publishing

GitHub Actions handles PyPI publishing (`.github/workflows/publish.yml`). Manual alternative: `just publish_pypi`.

A `noarch` conda package is also built on every `v*` tag and attached to the GitHub Release by `.github/workflows/conda-release.yml`. Local build instructions live in `docs/build.md`; the release flow is documented in `docs/conda-releasing.md`. A separate recipe prepared for a future submission to `conda-forge/staged-recipes` lives in `docs/misc/conda-forge-submission/`.
