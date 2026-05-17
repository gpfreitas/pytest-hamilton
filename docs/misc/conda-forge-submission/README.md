# Submitting `pytest-hamilton` to conda-forge

This directory contains a recipe ready to submit to
[`conda-forge/staged-recipes`](https://github.com/conda-forge/staged-recipes).
Nothing here is wired into CI or the local build — the canonical recipe
used by `just conda-build` and the GitHub Release workflow lives in
`recipe/recipe.yaml` at the repo root. This is a *staging area* for the
external submission.

## What gets submitted

```
recipes/
└── pytest-hamilton/
    └── recipe.yaml
```

A single recipe directory, dropped into a fork of `staged-recipes` under
its `recipes/` folder.

## Pre-submission checklist

`just publish_conda_forge` walks through steps 1–3 below interactively:
it prints the instructions, waits for you to edit the recipe and
confirm with ENTER, then runs `rattler-build` against the updated
recipe. The longhand below is kept for reference and for cases where
you want to do the steps by hand.

Before opening the PR, walk through these steps:

1. **The version on PyPI**. The recipe builds from the PyPI sdist. Make
   sure the version in `recipe.yaml` (`context.version`) corresponds to
   an actual release at <https://pypi.org/project/pytest-hamilton/>.

2. **Update the `sha256`**. From the project root:

   ```sh
   # Download the sdist that will actually be on PyPI and hash it
   VERSION=$(grep -m1 '^version' pyproject.toml | sed -E 's/version = "(.*)"/\1/')
   curl -sSL "https://pypi.org/packages/source/p/pytest-hamilton/pytest_hamilton-${VERSION}.tar.gz" \
       | shasum -a 256
   ```

   Paste the hash into `source.sha256`.

3. **Build it locally** to confirm the recipe works against the PyPI
   sdist (not the local checkout):

   ```sh
   rattler-build build --recipe docs/misc/conda-forge-submission/recipes/pytest-hamilton/recipe.yaml
   ```

4. **Maintainers**. `extra.recipe-maintainers` lists conda-forge GitHub
   usernames who can merge PRs to the future feedstock. Add co-maintainers
   here before submitting if anyone else has agreed to help.

## Submission steps

1. Fork <https://github.com/conda-forge/staged-recipes> on GitHub.
2. Clone your fork and create a branch:

   ```sh
   git clone git@github.com:<your-user>/staged-recipes.git
   cd staged-recipes
   git checkout -b add-pytest-hamilton
   ```

3. Copy the recipe from this repo into the fork:

   ```sh
   cp -R <path-to>/pytest-hamilton/docs/misc/conda-forge-submission/recipes/pytest-hamilton \
         recipes/
   ```

4. Commit and push:

   ```sh
   git add recipes/pytest-hamilton
   git commit -m "Add pytest-hamilton recipe"
   git push -u origin add-pytest-hamilton
   ```

5. Open a PR against `conda-forge/staged-recipes`. The PR template asks
   you to tick a few boxes (e.g. "I have read the conda-forge user
   docs"); most are self-evident for a pure-Python pytest plugin.

## After the PR is merged

- A feedstock is auto-created at `conda-forge/pytest-hamilton-feedstock`.
- conda-forge CI builds and uploads `pytest-hamilton` to the
  `conda-forge` channel on anaconda.org.
- For every subsequent PyPI release,
  [`regro-cf-autotick-bot`](https://github.com/regro/cf-scripts) opens a
  PR to the feedstock that bumps `context.version` and `source.sha256`.
  Review and merge to ship.
- Non-mechanical edits (new runtime dep, Python floor bump, build script
  change) require a manual PR to the feedstock.

## Why two recipes?

The recipe here and `recipe/recipe.yaml` at the repo root cover different
distribution channels and have different conventions:

| | `recipe/recipe.yaml` | `docs/misc/.../recipe.yaml` |
|---|---|---|
| Source | local checkout (`path: ..`) | PyPI sdist + sha256 |
| Version | injected from `pyproject.toml` via `PKG_VERSION` env var | hardcoded, bot-bumped |
| Built by | `just conda-build` and `conda-release.yml` | conda-forge feedstock CI |
| Where artifact lands | GitHub Release for the tag | conda-forge channel on anaconda.org |

Keeping them separate matches each channel's conventions and avoids
overloading one recipe with branching logic.
