# pytest-hamilton

![PyPI version](https://img.shields.io/pypi/v/pytest-hamilton.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`pytest-hamilton` is a pytest plugin that turns every node in an
[Apache Hamilton](https://github.com/dagworks-inc/hamilton) DAG into a
ready-to-use pytest fixture — with zero boilerplate in your test files.

Write a Hamilton module, point the plugin at it, and your tests can
request any computed node by name, exactly like any other fixture.

---

## Installation

```bash
pip install pytest-hamilton
```

The plugin is auto-discovered by pytest via the `pytest11` entry point.
No `conftest.py` changes are required in your project.

---

## Quick Start

Suppose you have a data pipeline in `lib_model.py`:

```python
# lib_model.py
import pandas as pd

def features(raw_data: pd.DataFrame) -> pd.DataFrame:
    return raw_data[["chas", "nox", "rm"]]

def labels(raw_data: pd.DataFrame) -> pd.Series:
    return raw_data["medv"]

def model_inputs(features: pd.DataFrame, labels: pd.Series) -> dict:
    return {"X": features, "y": labels}
```

Create an input config file:

```json
{"raw_data": "..."}
```

> **Note** For complex Python objects (like DataFrames) you will want to
> override `input_config` in your own `conftest.py` — see
> [Overriding `input_config`](#overriding-input_config) below.

Then write tests using any DAG node as a fixture argument:

```python
# test_lib_model.py

def test_features_shape(features):
    assert features.shape[1] == 3

def test_labels_are_positive(labels):
    assert (labels > 0).all()

def test_model_inputs_keys(model_inputs):
    assert "X" in model_inputs
    assert "y" in model_inputs
```

Run pytest with the plugin options:

```bash
pytest --hamilton-modules=lib_model --hamilton-config=test_inputs.json
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
[`Driver`](https://hamilton.dagworks.io/en/latest/reference/drivers/Driver/)
for the test session.  Useful for asserting things about the DAG itself
(e.g. node existence, metadata).

```python
def test_dag_has_features_node(hamilton_fixture_driver):
    names = {n.name for n in hamilton_fixture_driver.list_available_variables()}
    assert "features" in names
```

Skips the test automatically when no modules have been configured.

### `input_config` (function-scoped, overridable)

The dict of inputs loaded from the JSON config file.  Returns `{}` when
no config path is given.

### `hamilton_fixtures` (function-scoped)

The raw dict returned by `driver.execute()` for the subset of DAG nodes
requested by the current test.  Individual node fixtures (`features`,
`labels`, …) are thin wrappers around this.

---

## Overriding `input_config`

`input_config` is an ordinary pytest fixture and can be overridden in
your project's `conftest.py`.  This is the recommended way to supply
inputs that can't easily be expressed as JSON (DataFrames, database
connections, etc.):

```python
# conftest.py
import pytest
import pandas as pd

@pytest.fixture
def input_config(tmp_path):
    """Build a small in-memory DataFrame as the DAG input."""
    df = pd.DataFrame({
        "chas": [0, 1, 0],
        "nox":  [0.5, 0.6, 0.7],
        "rm":   [6.0, 6.5, 7.0],
        "medv": [20.0, 25.0, 30.0],
    })
    return {"raw_data": df}
```

Your override shadows the default file-loading behaviour for every test
in its scope.

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
uv run --python=3.13 --extra test pytest tests/
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

Built with [Hamilton](https://github.com/dagworks-inc/hamilton) by
DAGWorks and the excellent
[pytest-plugin cookiecutter](https://github.com/pytest-dev/cookiecutter-pytest-plugin)
as a structural reference.
