# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report bugs at https://github.com/gpfreitas/pytest_hamilton/issues.

If you are reporting a bug, please include:

- Your operating system name and version.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help wanted" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement" and "help wanted" is open to whoever wants to implement it.

### Write Documentation

Pytest Hamilton could always use more documentation, whether as part of the official docs, in docstrings, or even on the web in blog posts, articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue at https://github.com/gpfreitas/pytest_hamilton/issues.

If you are proposing a feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.
- Remember that this is a volunteer-driven project, and that contributions are welcome :)

## Get Started!

Ready to contribute? Here's how to set up `pytest-hamilton` for local development.

### Prerequisites

You need two tools installed on your machine before anything else:

| Tool | Purpose | Install |
|---|---|---|
| [uv](https://docs.astral.sh/uv/) | Python version management and dependency installation | [installation guide](https://docs.astral.sh/uv/getting-started/installation/) |
| [just](https://just.systems) | Task runner (`just qa`, `just test`, …) | [installation guide](https://just.systems/man/en/packages.html) |

Everything else — pytest, ruff, ty, coverage, ipdb — is installed automatically
by `uv` as part of step 3 below. You do not need to install them separately.

### Steps

1. Fork the `pytest-hamilton` repo on GitHub.
2. Clone your fork locally:

   ```sh
   git clone git@github.com:your_name_here/pytest-hamilton.git
   ```

3. Install the project and its dev dependencies:

   ```sh
   cd pytest-hamilton
   uv sync --extra test
   ```

4. Create a branch for local development:

   ```sh
   git checkout -b name-of-your-bugfix-or-feature
   ```

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass linting and the tests:

   ```sh
   just qa        # format + lint + type-check + test (Python 3.13)
   just testall   # run tests across all supported Python versions (3.10–3.13)
   ```

6. Commit your changes and push your branch to GitHub:

   ```sh
   git add .
   git commit -m "Your detailed description of your changes."
   git push origin name-of-your-bugfix-or-feature
   ```

7. Submit a pull request through the GitHub website.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put your new functionality into a function with a docstring, and add the feature to the list in README.md.
3. The pull request should work for Python 3.12 and 3.13. Tests run in GitHub Actions on every pull request to the main branch, make sure that the tests pass for all supported Python versions.

## Tips

To run a subset of tests:

```sh
just test tests/test_pytest_hamilton.py
```

## Deploying

A reminder for the maintainers on how to deploy. Make sure all your changes are committed (including an entry in HISTORY.md). Then run:

```sh
uv version patch  # or: minor, major
git commit -am "Release X.Y.Z"
just tag
```

GitHub Actions will automatically publish to PyPI when the tag is pushed. See `.github/workflows/publish.yml` for details.

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.
