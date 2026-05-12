# Conda release flow

This document covers how `pytest-hamilton` ships a `.conda` artifact with
every GitHub Release. The Python wheel/sdist PyPI flow is documented
separately in [`releasing.md`](releasing.md).

## How it works

Every git tag matching `v*` triggers **two** parallel workflows:

| Workflow | Output |
|---|---|
| `.github/workflows/publish.yml` | wheel + sdist → PyPI |
| `.github/workflows/conda-release.yml` | `.conda` → GitHub Release for the tag |

The conda workflow:

1. Checks out the tagged commit.
2. Derives the version from `${GITHUB_REF_NAME}` (strips the leading `v`).
3. Verifies that derived version equals the `version` field in
   `pyproject.toml` — fails the build if they disagree.
4. Builds the `noarch` package with `rattler-build` from `recipe/recipe.yaml`.
5. Attaches the resulting `.conda` to the GitHub Release for the tag
   (creating the Release if it doesn't already exist) via
   `softprops/action-gh-release`.

No external credentials are needed — the workflow uses only
`GITHUB_TOKEN` (with `contents: write`) to upload to its own Release.

## How users install from a GitHub Release

```sh
# Download the .conda from the GitHub Release page, then:
conda install -c conda-forge ./pytest-hamilton-<version>-<hash>.conda
```

Or, with `mamba` / `pixi` global:

```sh
mamba install -c conda-forge ./pytest-hamilton-<version>-<hash>.conda
```

The `-c conda-forge` flag is needed so the package's runtime dependencies
(`pytest`, `sf-hamilton`) resolve from conda-forge.

## Normal release workflow

Same as the PyPI flow — there's nothing extra to do for the conda
artifact. See [`releasing.md`](releasing.md) for the version-bump and tag
sequence. Pushing the `vX.Y.Z` tag fires both workflows in parallel.

Monitor the conda run at
`https://github.com/gpfreitas/pytest-hamilton/actions/workflows/conda-release.yml`.

## Building locally

For instructions on producing a `.conda` on your own machine (useful for
testing recipe changes before tagging), see [`build.md`](build.md).

## Relationship to conda-forge

The artifact published to GitHub Releases is **not** the same as the
artifact users will get from `conda install -c conda-forge
pytest-hamilton` once the package is on conda-forge. They are built from
different recipes:

- The GitHub Release `.conda` comes from `recipe/recipe.yaml`.
- The conda-forge `.conda` will come from the
  `conda-forge/pytest-hamilton-feedstock` repo, populated initially from
  the recipe under `docs/misc/conda-forge-submission/`.

The GitHub-Release artifact serves users who want it before (or instead
of) conda-forge availability, and provides a reproducible artifact tied
to a specific tagged commit.
