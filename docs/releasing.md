# Releasing to PyPI

This document covers everything needed to publish `pytest-hamilton` to PyPI —
both the one-time setup and the normal release workflow.

## How it works

Publishing uses two tools, both already configured in this repo:

- **`uv build`** — builds the sdist and wheel from `pyproject.toml`
- **`pypa/gh-action-pypi-publish`** — uploads the built artifacts to PyPI
  using [OIDC Trusted Publishers](https://docs.pypi.org/trusted-publishers/),
  which means no API tokens or credentials are stored anywhere

The trigger is a `v*` git tag. Pushing one causes
`.github/workflows/publish.yml` to run automatically.

---

## One-time setup (first release only)

### 1. Create the PyPI project

The Trusted Publisher mechanism requires the project to already exist on PyPI
before it can be used. Do a one-time manual publish to create it:

```sh
uv build
UV_PUBLISH_TOKEN=pypi-<your-token> uv publish
```

Generate an API token at <https://pypi.org/manage/account/token/> (scope it to
the new project after the first upload creates it).

### 2. Configure the OIDC Trusted Publisher

Once the project exists on PyPI, replace token-based auth with the more secure
OIDC approach:

1. Go to <https://pypi.org/manage/project/pytest-hamilton/settings/publishing/>
2. Add a new Trusted Publisher with these values:

   | Field | Value |
   |---|---|
   | Owner | `gpfreitas` |
   | Repository | `pytest-hamilton` |
   | Workflow name | `publish.yml` |
   | Environment | *(leave blank)* |

After this, the GitHub Actions workflow can publish without any stored secret.
The `id-token: write` permission already present in `publish.yml` is all it
needs.

---

## Normal release workflow

After the one-time setup, every release follows the same steps:

### 1. Prepare the release commit

Make sure all changes are merged to `main` and the test suite is green:

```sh
just qa
just testall   # optional: run across all supported Python versions
```

Update `HISTORY.md` with a summary of changes for this version.

### 2. Bump the version

```sh
uv version patch   # 0.1.0 → 0.1.1
# or:
uv version minor   # 0.1.0 → 0.2.0
# or:
uv version major   # 0.1.0 → 1.0.0
```

This updates the `version` field in `pyproject.toml` in place.

### 3. Commit and tag

```sh
git commit -am "Release $(uv version --short)"
just tag
```

`just tag` creates an annotated git tag (`v0.1.1`) and pushes it to GitHub.

### 4. GitHub Actions takes over

Pushing the tag triggers `.github/workflows/publish.yml`:

1. `uv build` — produces `dist/pytest_hamilton-X.Y.Z-py3-none-any.whl`
   and `dist/pytest_hamilton-X.Y.Z.tar.gz`
2. `pypa/gh-action-pypi-publish` — uploads both artifacts to PyPI via OIDC

Monitor the run at
`https://github.com/gpfreitas/pytest-hamilton/actions/workflows/publish.yml`.

---

## Manual publishing fallback

If you need to publish outside GitHub Actions (e.g. to fix a botched release,
or before OIDC is configured), use `just publish_pypi`:

```sh
just publish_pypi   # runs: uv build && uv publish
```

`uv publish` needs PyPI credentials. Supply them via environment variable:

```sh
UV_PUBLISH_TOKEN=pypi-<your-token> just publish_pypi
```

Or configure `~/.pypirc` and uv will read it automatically.

---

## Publishing to TestPyPI

To verify the build and metadata before a real release:

```sh
uv build
UV_PUBLISH_URL=https://test.pypi.org/legacy/ \
UV_PUBLISH_TOKEN=pypi-<your-testpypi-token> \
uv publish
```

Check the result at <https://test.pypi.org/project/pytest-hamilton/>.
