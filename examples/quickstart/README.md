# quickstart example

This directory contains the working example from the [top-level README](../../README.md).
It implements a small Hamilton data pipeline and shows how `pytest-hamilton` turns
every DAG node into a ready-to-use pytest fixture.

## Files

| File | Purpose |
|---|---|
| `lib_model.py` | Hamilton module — defines `features`, `labels`, and `model_inputs` nodes |
| `conftest.py` | Overrides `input_config` with an in-memory DataFrame |
| `test_lib_model.py` | Four tests, one per fixture / DAG node |
| `pyproject.toml` | Sets `hamilton_modules = lib_model` so no CLI flags are needed |

## Why `conftest.py` instead of a JSON config?

The README quickstart shows `--hamilton-config=test_inputs.json`, but the
pipeline's root input (`raw_data`) is a pandas DataFrame, which cannot be
expressed in JSON. Overriding `input_config` in `conftest.py` is the
recommended approach for any input that isn't a JSON primitive — see the
[Overriding `input_config`](../../README.md#overriding-input_config) section
of the README.

## Running the tests

The plugin and its dependencies are installed at the repository root, so
run pytest from there:

```sh
# from the repository root
uv run --python=3.13 --extra test pytest examples/quickstart/ -v
```

Expected output:

```
collected 4 items

examples/quickstart/test_lib_model.py::test_features_shape       PASSED
examples/quickstart/test_lib_model.py::test_labels_are_positive  PASSED
examples/quickstart/test_lib_model.py::test_model_inputs_keys    PASSED
examples/quickstart/test_lib_model.py::test_dag_has_features_node PASSED

4 passed in 0.02s
```

## What each test checks

| Test | Fixture | Assertion |
|---|---|---|
| `test_features_shape` | `features` | DataFrame has exactly 3 columns (`chas`, `nox`, `rm`) |
| `test_labels_are_positive` | `labels` | All `medv` values are positive |
| `test_model_inputs_keys` | `model_inputs` | Dict has keys `X` and `y` |
| `test_dag_has_features_node` | `hamilton_fixture_driver` | DAG exposes a node named `features` |
