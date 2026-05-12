# Installation

## From GitHub

Until the first PyPI release, install directly from the GitHub repository:

```sh
uv add "git+https://github.com/gpfreitas/pytest-hamilton"
```

Or with `pip`:

```sh
pip install "git+https://github.com/gpfreitas/pytest-hamilton"
```

## From source

The source files for pytest-hamilton can be downloaded from the [GitHub repo](https://github.com/gpfreitas/pytest-hamilton).

You will need [uv](https://docs.astral.sh/uv/) installed first
([installation guide](https://docs.astral.sh/uv/getting-started/installation/)).
All other dependencies are managed by uv.

You can either clone the public repository:

```sh
git clone git@github.com:gpfreitas/pytest-hamilton.git
```

Or download the [tarball](https://github.com/gpfreitas/pytest-hamilton/tarball/main):

```sh
curl -OJL https://github.com/gpfreitas/pytest-hamilton/tarball/main
```

Once you have a copy of the source, you can install it with:

```sh
cd pytest-hamilton
uv sync --extra test
```
