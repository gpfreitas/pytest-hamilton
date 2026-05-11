**This project has not been released yet, but it is usable. Install it straight from GitHub for now.**

---

# pytest-hamilton

![PyPI version](https://img.shields.io/pypi/v/pytest-hamilton.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`pytest-hamilton` is a pytest plugin that turns every node in an
[Apache Hamilton](https://github.com/apache/hamilton) DAG into a
ready-to-use pytest fixture — with zero boilerplate in your test files.

Write a Hamilton module, point the plugin at it, and your tests can
request any computed node by name, exactly like any other fixture.

---

## Installation

```bash
uv pip install "git+https://github.com/gpfreitas/pytest-hamilton"
```

The plugin is auto-discovered by pytest via the `pytest11` entry point.
No `conftest.py` changes are required in your project.

---

## Quick Start

Suppose you have a small DAG in `lib_model.py`:

```python
# lib_model.py

def x_plus_y(x: int, y: int) -> int:
    return x + y

def final(x_plus_y: int) -> int:
    return x_plus_y**2
```

Create an input config file `config.json`:

```json
{"x": 2, "y": 3}
```

Then write tests using any DAG node as a fixture argument:

```python
# test_lib_model.py

def test_x_plus_y(x_plus_y, x, y):
    assert x_plus_y - x == y

def test_final(final, x_plus_y):
    factor = final / x_plus_y
    assert factor == x_plus_y
```

Run pytest with the plugin options:

```bash
pytest --hamilton-modules=lib_model --hamilton-config=config.json
```

That's it. No `conftest.py`. No manually written fixtures.

---

## Configuration

Options can be set on the command line **or** in `pyproject.toml` /
`pytest.ini` (CLI takes precedence).

| ini option | CLI flag | Description |
|---|---|---|
| `hamilton_modules` | `--hamilton-modules` | Comma-separated dotted module paths containing Hamilton DAG functions (e.g. `mypackage.lib_model,mypackage.transforms`) |
| `hamilton_config` | `--hamilton-config` | Path to a JSON file that supplies input values to the Hamilton DAG |

**Example `pyproject.toml` configuration:**

```toml
[tool.pytest.ini_options]
hamilton_modules = "lib_model"
hamilton_config  = "tests/fixtures/test_inputs.json"
```

With this in place you can just run `pytest` — no flags needed.

**Disabling the plugin** for a single run:

```bash
pytest -p no:hamilton
```

---

## Provided Fixtures

### `hamilton_fixture_driver` (session-scoped)

The underlying Hamilton
[`Driver`](https://hamilton.apache.org/en/latest/reference/drivers/Driver/)
for the test session.  Useful for asserting things about the DAG itself
(e.g. node existence, metadata).

```python
def test_dag_has_features_node(hamilton_fixture_driver):
    names = {n.name for n in hamilton_fixture_driver.list_available_variables()}
    assert "features" in names
```

Skips the test automatically when no modules have been configured.

### `input_config` (function-scoped)

The dict of inputs loaded from the JSON config file.  Returns `{}` when
no config path is given.

### `hamilton_fixtures` (function-scoped)

The raw dict returned by `driver.execute()` for the subset of DAG nodes
requested by the current test.  Individual node fixtures (`features`,
`labels`, …) are thin wrappers around this.

---

## Testing pytest-hamilton itself

This repo's own test suite uses pytest's built-in
[`pytester`](https://docs.pytest.org/en/stable/reference/fixtures.html#pytester)
fixture to run full sub-process pytest sessions and verify outcomes.

### Prerequisites

You need [uv](https://docs.astral.sh/uv/) and [just](https://just.systems)
installed. All other dev tools (pytest, ruff, ty, …) are managed by uv and
installed automatically when you run `uv sync --extra test`.

`pytester` is enabled in `tests/conftest.py`:

```python
# tests/conftest.py
pytest_plugins = ["pytester"]
```

### Running the tests

```bash
# Using just (recommended):
just test

# Or directly with uv:
uv run --python=3.14 --extra test pytest tests/
```

### How the tests work

Each test case:

1. Calls `pytester.makepyfile(sample_module=...)` to create a minimal
   Hamilton module in a temporary sandbox directory.
2. Optionally creates a JSON config file with `pytester.makefile(...)`.
3. Creates a test file in the sandbox with `pytester.makepyfile(...)`.
4. Runs `pytester.runpytest_subprocess(...)` — spawns a fresh pytest
   process so the plugin is loaded from scratch, with no shared state.
5. Asserts the expected outcomes with `result.assert_outcomes(...)`.

See `tests/test_pytest_hamilton.py` for the full test suite.

---

## License

MIT — see [LICENSE](LICENSE).

## Credits

Built with [Apache Hamilton](https://github.com/apache/hamilton) and the excellent
[pytest-plugin cookiecutter](https://github.com/pytest-dev/cookiecutter-pytest-plugin)
as a structural reference.
