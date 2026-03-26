# Installation

## Stable release

To install Pytest Hamilton, run this command in your terminal:

```sh
uv add pytest-hamilton
```

Or if you prefer to use `pip`:

```sh
pip install pytest-hamilton
```

## From source

The source files for pytest-hamilton can be downloaded from the [Github repo](https://github.com/gpfreitas/pytest-hamilton).

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
