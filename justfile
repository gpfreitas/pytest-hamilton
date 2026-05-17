# Justfile for pytest-hamilton — single-Python contributor verbs.
# Matrix work is delegated to `nox` via `uvx`. See AGENTS.md "Tooling philosophy".

DEFAULT_PYTHON := "3.14"
VERSION := `grep -m1 '^version' pyproject.toml | sed -E 's/version = "(.*)"/\1/'`

# Show available commands
list:
	@just --list

# Run all the formatting, linting, and testing commands (single Python)
qa:
	uv run --python={{DEFAULT_PYTHON}} --extra test ruff format .
	uv run --python={{DEFAULT_PYTHON}} --extra test ruff check . --fix
	uv run --python={{DEFAULT_PYTHON}} --extra test ty check .
	uv run --python={{DEFAULT_PYTHON}} --extra test pytest

# Run the plugin's own test suite across all supported Pythons (via nox)
testall:
	uvx nox -s tests

# Run each example template across all supported Pythons (via nox)
test_examples:
	uvx nox -s test_examples

# Run all the tests, but allow for arguments to be passed
test *ARGS:
	@echo "Running with arg: {{ARGS}}"
	uv run --python={{DEFAULT_PYTHON}} --extra test pytest {{ARGS}}

# Run all the tests, but on failure, drop into the debugger
pdb *ARGS:
	@echo "Running with arg: {{ARGS}}"
	uv run --python={{DEFAULT_PYTHON}} --extra test pytest --pdb --maxfail=10 --pdbcls=IPython.terminal.debugger:TerminalPdb {{ARGS}}

# Run coverage, and build to HTML
coverage:
	uv run --python={{DEFAULT_PYTHON}} --extra test coverage run -m pytest tests
	uv run --python={{DEFAULT_PYTHON}} --extra test coverage report -m
	uv run --python={{DEFAULT_PYTHON}} --extra test coverage html

# Build the project, useful for checking that packaging is correct
build:
	rm -rf build
	rm -rf dist
	uv build

# Build the conda package (noarch, single artifact). Requires rattler-build on PATH.
# Install with: brew install rattler-build  (or)  conda install -c conda-forge rattler-build
conda-build:
	rm -rf dist/conda
	PKG_VERSION={{VERSION}} rattler-build build --recipe recipe/recipe.yaml --output-dir dist/conda

# Print the current version of the project
version:
	@echo "Current version is {{VERSION}}"

# Tag the current version in git and put to github
tag:
	echo "Tagging version v{{VERSION}}"
	git tag -a v{{VERSION}} -m "Creating version v{{VERSION}}"
	git push origin v{{VERSION}}

# remove all build, test, coverage and Python artifacts
clean: clean-build clean-pyc clean-test

# remove build artifacts
clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

# remove Python file artifacts
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

# remove test and coverage artifacts
clean-test:
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

# Publish to PyPI (manual alternative to GitHub Actions). Default target is TestPyPI; pass `prod` for real PyPI.
publish_pypi target="test":
	uv build
	{{ if target == "test" { "UV_PUBLISH_URL=https://test.pypi.org/legacy/ uv publish" } else { "uv publish" } }}

# Walk through a conda-forge submission interactively: print the manual edit steps, wait for confirmation, then build the recipe locally with rattler-build. Requires rattler-build on PATH. Does NOT push or open a PR.
publish_conda_forge:
	#!/usr/bin/env bash
	set -euo pipefail
	RECIPE="docs/misc/conda-forge-submission/recipes/pytest-hamilton/recipe.yaml"
	SDIST_URL="https://pypi.org/packages/source/p/pytest-hamilton/pytest_hamilton-{{VERSION}}.tar.gz"

	echo "==> Conda-forge submission prep for pytest-hamilton {{VERSION}}"
	echo ""
	echo "This is a guided one-time submission. After the recipe is merged to"
	echo "conda-forge/staged-recipes, version bumps on the auto-created feedstock"
	echo "are handled by regro-cf-autotick-bot — you should not need this recipe"
	echo "again for normal releases."
	echo ""
	echo "Step 1: Verify the version is on PyPI"
	echo "    The recipe builds from the PyPI sdist, so {{VERSION}} must already"
	echo "    be published. Check:"
	echo "        https://pypi.org/project/pytest-hamilton/{{VERSION}}/"
	echo ""
	echo "Step 2: Edit the recipe"
	echo "    Open: $RECIPE"
	echo ""
	echo "    Update two fields:"
	echo "      - context.version  (around line 20): set to \"{{VERSION}}\""
	echo "      - source.sha256    (around line 29): see Step 3"
	echo ""
	echo "Step 3: Compute and paste the sha256"
	echo "    The sha256 pins the build to the exact sdist bytes that were on"
	echo "    PyPI when the recipe was authored. conda-forge CI downloads"
	echo "    source.url and refuses to build if the hash does not match."
	echo ""
	echo "    Compute it with:"
	echo "        curl -sSL \"$SDIST_URL\" | shasum -a 256"
	echo ""
	echo "    Paste the resulting 64-character hex string into source.sha256."
	echo ""
	echo "Step 4 (optional): Confirm maintainers"
	echo "    extra.recipe-maintainers (bottom of the file) lists the conda-forge"
	echo "    GitHub usernames who can merge feedstock PRs. Add co-maintainers"
	echo "    here if anyone else has agreed to help."
	echo ""
	echo "Documentation:"
	echo "    Local checklist:  docs/misc/conda-forge-submission/README.md"
	echo "    conda-forge docs: https://conda-forge.org/docs/maintainer/adding_pkgs/"
	echo ""

	read -r -p "Press ENTER when the recipe file is edited and ready for us to continue (Ctrl-C to abort)..."

	echo ""
	echo "==> Building the recipe locally with rattler-build"
	rm -rf dist/conda-forge
	rattler-build build --recipe "$RECIPE" --output-dir dist/conda-forge

	echo ""
	echo "==> Local prep complete. Remaining manual steps:"
	echo "    1. Review and commit the diff in $RECIPE"
	echo "    2. Fork https://github.com/conda-forge/staged-recipes"
	echo "    3. Copy that recipe directory into your fork at recipes/pytest-hamilton/"
	echo "    4. Commit, push, and open a PR against conda-forge/staged-recipes"
	echo "    See docs/misc/conda-forge-submission/README.md for the full checklist."
