# Conda packaging

`pytest-hamilton` is distributed on [conda-forge](https://conda-forge.org)
in addition to PyPI. conda users can install it with:

```sh
conda install conda-forge::pytest-hamilton
# or, if conda-forge is already in your channels:
conda install pytest-hamilton
```

This document covers the one-time submission to conda-forge and how to keep
the feedstock up to date with new releases.

---

## How it works

conda-forge builds packages from the PyPI source distribution (sdist). The
recipe in `recipe/meta.yaml` tells conda-forge:

- where to download the source (PyPI URL)
- how to verify it (SHA-256 hash)
- how to build it (`pip install --no-deps`)
- what its runtime dependencies are
- how to test the installed package

The recipe lives in two places:

| Location | Purpose |
|---|---|
| `recipe/meta.yaml` in **this repo** | Authoritative draft; updated here first on each release |
| `recipe/meta.yaml` in [conda-forge/pytest-hamilton-feedstock](https://github.com/conda-forge/pytest-hamilton-feedstock) | What conda-forge actually builds from |

---

## Prerequisite: publish to PyPI first

conda-forge downloads the sdist from PyPI, so the package must be published
there before a conda-forge build can succeed. Follow the steps in
[docs/releasing.md](releasing.md) to do a PyPI release, then come back here.

---

## First-time submission to conda-forge

This only needs to happen once. After it's done, subsequent releases are
much simpler (see the next section).

### 1. Fill in the SHA-256 hash

After publishing to PyPI, get the hash of the sdist:

```sh
sha256sum dist/pytest_hamilton-X.Y.Z.tar.gz
```

Or copy it from the PyPI page:
`https://pypi.org/project/pytest-hamilton/X.Y.Z/#files` → click the
SHA-256 link next to the `.tar.gz` entry.

Update `recipe/meta.yaml` — replace `sha256: FIXME` with the real hash
and bump `version` if needed. Commit to the `add_conda` branch.

### 2. Fork conda-forge/staged-recipes

```sh
# Fork https://github.com/conda-forge/staged-recipes on GitHub, then:
git clone git@github.com:your_name_here/staged-recipes.git
cd staged-recipes
git checkout -b add-pytest-hamilton
```

### 3. Add the recipe

```sh
mkdir -p recipes/pytest-hamilton
cp /path/to/pytest-hamilton/recipe/meta.yaml recipes/pytest-hamilton/
```

### 4. Open the pull request

Push the branch and open a PR against `conda-forge/staged-recipes:main`.
The PR template includes a checklist — the key items are:

- [ ] License is correctly identified (`MIT`)
- [ ] `license_file` points to an existing file (`LICENSE`)
- [ ] Tests pass (imports + `pip check` + `pytest --help`)
- [ ] `noarch: python` is set (pure-Python package)
- [ ] Your GitHub username is in `recipe-maintainers`

CI will build the package on Linux, macOS, and Windows. Maintainers will
review and merge once everything is green.

### 5. After the PR is merged

conda-forge automatically creates a new repository:
`https://github.com/conda-forge/pytest-hamilton-feedstock`

You will be added as a maintainer. Future release updates happen there.

---

## Updating the feedstock for new releases

### Automatic updates (the easy path)

conda-forge runs a bot (`regro-cf-autotick-bot`) that monitors PyPI for new
releases. When a new version of `pytest-hamilton` appears on PyPI, the bot
usually opens a PR on the feedstock within a day or two, updating `version`
and `sha256` automatically. Review the PR, confirm the tests pass, and merge.

### Manual updates

If the bot doesn't open a PR, or if you need to change the recipe (e.g. add
a new dependency), update the feedstock yourself:

1. Fork `conda-forge/pytest-hamilton-feedstock`
2. Edit `recipe/meta.yaml`:
   - Bump `version`
   - Update `sha256` (from `sha256sum dist/pytest_hamilton-X.Y.Z.tar.gz`)
   - Reset `build.number` to `0`
   - Update any changed dependencies
3. Open a PR against the feedstock's `main` branch

Also keep `recipe/meta.yaml` in **this repo** in sync — it is the source
of truth for the recipe before it lands in the feedstock.

---

## Testing the recipe locally

Before submitting to staged-recipes, you can verify the recipe builds
correctly on your machine:

```sh
# Requires conda-build in your base environment
conda install -n base conda-build

# Build from the recipe/ directory
conda build recipe/

# Install the locally built package to test it
conda install --use-local pytest-hamilton
```

This catches recipe errors (wrong sha256, missing deps, failed tests) before
CI does.
