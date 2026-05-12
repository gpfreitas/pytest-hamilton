# Building locally

This document covers how to produce the two artifact types that
`pytest-hamilton` ships:

- a **Python wheel + sdist** (uploaded to PyPI by CI)
- a **conda package** (`.conda`, attached to each GitHub Release by CI)

For the *release* flows (what CI does on a tag) see
[`releasing.md`](releasing.md) and [`conda-releasing.md`](conda-releasing.md).
This doc is about building artifacts on your own machine.

---

## Python wheel + sdist

No prerequisites beyond `uv` and `just`, both already required for the
project's normal dev loop.

```sh
just build
```

This wipes `build/` and `dist/`, then runs `uv build`, producing:

```
dist/
├── pytest_hamilton-<version>-py3-none-any.whl
└── pytest_hamilton-<version>.tar.gz
```

You can install the wheel into any environment to smoke-test it:

```sh
uv pip install dist/pytest_hamilton-<version>-py3-none-any.whl
```

---

## Conda package

The conda artifact is a **`noarch: python`** package — one file that works
on Linux, macOS, and Windows for any supported Python version. It is built
with [rattler-build](https://rattler.build/) from `recipe/recipe.yaml`.

### Prerequisites

You need `rattler-build` on your `PATH`. Any of these install methods work:

| Platform | Command |
|---|---|
| macOS (recommended) | `brew install rattler-build` |
| Linux / macOS / Windows, via conda | `conda install -c conda-forge rattler-build` |
| Linux / macOS / Windows, via pixi | `pixi global install rattler-build` |
| Any platform with Rust toolchain | `cargo install rattler-build --locked` |

Verify the install:

```sh
rattler-build --version
```

### Build

```sh
just conda-build
```

What it does:

1. Removes `dist/conda/`.
2. Reads the project version from `pyproject.toml` and passes it to the
   recipe via the `PKG_VERSION` env var.
3. Runs `rattler-build build --recipe recipe/recipe.yaml --output-dir
   dist/conda`.

Output:

```
dist/conda/
└── noarch/
    └── pytest-hamilton-<version>-<build-string>.conda
```

`rattler-build` also runs the recipe's `tests:` section after the build —
import-checks plus `pip check` — so a successful build means the package
is at minimum importable in a fresh env.

### Manually testing the .conda

```sh
# Create a throwaway env from the freshly-built artifact
conda create -n pth-smoke -c conda-forge --override-channels \
    dist/conda/noarch/pytest-hamilton-*.conda python=3.12

conda run -n pth-smoke python -c "import pytest_hamilton; print('ok')"
conda env remove -n pth-smoke
```

---

## How the two recipes relate

There are two conda recipes in the repo, intentionally:

- **`recipe/recipe.yaml`** — what `just conda-build` and the CI workflow
  use. Sources from the local checkout (`source: path: ..`), version is
  injected from `pyproject.toml`. Single source of truth.
- **`docs/misc/conda-forge-submission/recipes/pytest-hamilton/recipe.yaml`**
  — the recipe prepared for submission to
  [`conda-forge/staged-recipes`](https://github.com/conda-forge/staged-recipes).
  Sources from the PyPI sdist with a pinned `sha256`, version is
  hardcoded (conda-forge bots bump it automatically once the feedstock
  exists). See that directory's `README.md` for the submission process.
