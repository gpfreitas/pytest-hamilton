# example02 — DataFrame input via conftest.py override (polars)

A pytest-hamilton template for the common case where your DAG's root input
is a DataFrame (not a JSON primitive). The DataFrame is supplied by
overriding the `input_config` fixture in `conftest.py`.

## Use as a template

    cp -r examples/example02 ~/my-project
    cd ~/my-project
    # See "Editing pyproject.toml after copying" below before running uv sync.
    uv sync
    uv run pytest

## Editing `pyproject.toml` after copying

When you copy this folder to start a new project, make these edits to
`pyproject.toml`:

1. **Change `[project].name`** from `"example-02"` to your project's name.
2. **Delete the entire `[tool.uv.sources]` table.** It exists only so the
   pytest-hamilton repo's CI can install the plugin from the local
   checkout. Once removed, uv installs `pytest-hamilton` from PyPI as
   declared in `[project].dependencies`.
3. **Review `[project].dependencies`.** If your real project doesn't need
   polars, drop it; if it needs other libraries (pandas, numpy, etc.),
   add them.
4. *(Optional)* Update `description`, `version`, add `authors`, etc.

## Why `conftest.py` instead of a JSON config?

The DAG's root input (`raw_data`) is a polars DataFrame, which cannot be
expressed in JSON. Overriding `input_config` in `conftest.py` is the
recommended approach for any input that isn't a JSON primitive.

## Files

| File | Purpose |
|---|---|
| `pyproject.toml`     | Project metadata, deps, and pytest config |
| `lib_model.py`       | Hamilton module — `features`, `labels`, `model_inputs` |
| `conftest.py`        | Overrides `input_config` with an in-memory polars DataFrame |
| `test_lib_model.py`  | One test per node fixture, plus a DAG introspection test |

## Running the tests during pytest-hamilton development

From inside the example folder:

    cd examples/example02
    uv sync && uv run pytest

Or from the repo root, via nox (runs the full matrix):

    just examples
