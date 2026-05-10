# example01 — pytest-hamilton quickstart template

A complete, copy-pasteable pytest-hamilton project template. The DAG is
intentionally trivial (`x_plus_y = x + y`, `final = x_plus_y ** 2`); the
point is to show the wiring, not the math.

## Use as a template

    cp -r examples/example01 ~/my-project
    cd ~/my-project
    # See "Editing pyproject.toml after copying" below before running uv sync.
    uv sync
    uv run pytest

## Editing `pyproject.toml` after copying

When you copy this folder to start a new project, make these edits to
`pyproject.toml`:

1. **Change `[project].name`** from `"example-01"` to your project's name.
2. **Delete the entire `[tool.uv.sources]` table.** It exists only so the
   pytest-hamilton repo's CI can install the plugin from the local
   checkout. Once removed, uv installs `pytest-hamilton` from PyPI as
   declared in `[project].dependencies`.
3. *(Optional)* Update `description`, `version`, add `authors`, etc.

Everything else (`[project.optional-dependencies]`, `[tool.uv]`,
`[tool.pytest.ini_options]`) is template-ready and needs no changes.

## Files

| File | Purpose |
|---|---|
| `pyproject.toml`     | Project metadata, deps, and pytest config |
| `lib_model.py`       | Hamilton module — defines `x_plus_y` and `final` nodes |
| `config.json`        | Inputs (`x`, `y`) loaded via `hamilton_config` in pyproject.toml |
| `test_lib_model.py`  | One test per node fixture |

## Running the tests during pytest-hamilton development

From inside the example folder:

    cd examples/example01
    uv sync && uv run pytest

Or from the repo root, via nox (runs the full matrix):

    just examples
