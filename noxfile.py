"""Nox sessions: matrix-test the plugin and each example template.

Doctrine: just is the contributor-facing verb runner for single-Python
inner-loop tasks (qa, test, pdb, coverage). Nox owns the matrix.

Two sessions, two responsibilities:
- tests: the plugin's own test suite across all supported Pythons.
- test_examples: each examples/exampleNN/ in its own venv, parametrized
  over (Python, example). Each example has its own pyproject.toml that
  declares pytest-hamilton from PyPI; a [tool.uv.sources] block in each
  example pyproject redirects to the local checkout for dev only.
"""

from pathlib import Path

import nox

ROOT = Path(__file__).parent.resolve()
EXAMPLES_DIR = ROOT / "examples"
PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13", "3.14"]


def _example_ids() -> list[str]:
    return sorted(
        p.name
        for p in EXAMPLES_DIR.iterdir()
        if p.is_dir() and p.name.startswith("example")
    )


@nox.session(python=PYTHON_VERSIONS, venv_backend="uv")
def tests(session: nox.Session) -> None:
    """Run the plugin's own test suite across all supported Pythons."""
    session.run_install(
        "uv",
        "sync",
        "--active",
        "--extra",
        "test",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    session.run("pytest", "-v")


@nox.session(python=PYTHON_VERSIONS, venv_backend="uv")
@nox.parametrize("example", _example_ids())
def test_examples(session: nox.Session, example: str) -> None:
    """Run each examples/exampleNN/ in its own venv."""
    example_path = EXAMPLES_DIR / example
    session.run_install(
        "uv",
        "sync",
        "--project",
        str(example_path),
        "--active",
        "--extra",
        "test",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    with session.chdir(example_path):
        session.run("pytest", "-v")
