"""pytest-hamilton: automatic Hamilton-based fixtures for pytest."""

from __future__ import annotations

import importlib
import json
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

logger = logging.getLogger(__name__)

_PLUGIN_NAME = "hamilton_node_fixtures"


# ---------------------------------------------------------------------------
# Option registration
# ---------------------------------------------------------------------------


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register --hamilton-modules and --hamilton-config CLI flags and ini-options."""
    group = parser.getgroup("hamilton", "Hamilton-based automatic fixtures")
    group.addoption(
        "--hamilton-modules",
        action="store",
        default=None,
        help=(
            "Comma-separated Python module names containing Hamilton DAG functions. "
            "Overrides the 'hamilton_modules' ini option."
        ),
    )
    group.addoption(
        "--hamilton-config",
        action="store",
        default=None,
        help=(
            "Path to a JSON file with input values for the Hamilton DAG. Overrides the 'hamilton_config' ini option."
        ),
    )
    parser.addini(
        "hamilton_modules",
        help="Comma-separated Python module names containing Hamilton DAG functions.",
        default="",
    )
    parser.addini(
        "hamilton_config",
        help="Path to a JSON file with input values for the Hamilton DAG.",
        default="",
    )


def _get_hamilton_option(config: pytest.Config, name: str) -> str | None:
    """Return the CLI value if set, else the ini value, else None.

    CLI flags take precedence over ini-file options so that users can
    override project-level defaults on a per-run basis.
    """
    cli_flag = f"--hamilton-{name.replace('_', '-')}"
    cli_val: str | None = config.getoption(cli_flag, default=None)
    if cli_val:
        return cli_val
    ini_val: str = config.getini(f"hamilton_{name}")
    return ini_val if ini_val else None


# ---------------------------------------------------------------------------
# Plugin class: holds the driver and all dynamic per-node fixtures
# ---------------------------------------------------------------------------


class _HamiltonPlugin:
    """Registered with pytest's plugin manager to provide Hamilton-backed fixtures.

    Holds the Hamilton driver and exposes one function-scoped ``@pytest.fixture``
    per DAG node, each of which pulls its value from ``hamilton_fixtures``.
    The driver is stored as a plain instance attribute so that type checkers
    are happy and we do not need to stash anything on ``pytest.Config``.
    """

    def __init__(self, driver: Any) -> None:
        self.driver = driver


def _make_node_fixture(name: str) -> Callable[..., Any]:
    """Return a function-scoped fixture that extracts *name* from hamilton_fixtures."""

    @pytest.fixture(name=name)
    def _node_fixture(hamilton_fixtures: dict[str, Any]) -> Any:
        return hamilton_fixtures[name]

    _node_fixture.__name__ = name
    return _node_fixture


# ---------------------------------------------------------------------------
# Plugin configuration: build the driver and register the plugin
# ---------------------------------------------------------------------------


def pytest_configure(config: pytest.Config) -> None:
    """Build the Hamilton driver and register one fixture per DAG node.

    This hook runs early enough that the dynamically created fixtures are
    available during collection.  If no modules are configured the plugin
    is a complete no-op, so it never interferes with existing test suites.
    """
    modules_spec = _get_hamilton_option(config, "modules")
    if not modules_spec:
        return

    import hamilton.driver  # imported lazily; sf-hamilton is a runtime dep but not needed at import time

    module_names = [m.strip() for m in modules_spec.split(",") if m.strip()]
    modules = [importlib.import_module(name) for name in module_names]

    driver = hamilton.driver.Builder().with_config({}).with_modules(*modules).build()

    # Build the plugin object (stores the driver, receives dynamic fixtures below).
    plugin = _HamiltonPlugin(driver)

    # Attach one fixture per DAG node directly to the plugin instance so that
    # pytest discovers them when it inspects the plugin's attributes.
    for node in driver.list_available_variables():
        setattr(plugin, node.name, _make_node_fixture(node.name))

    config.pluginmanager.register(plugin, name=_PLUGIN_NAME)


# ---------------------------------------------------------------------------
# Public fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def hamilton_fixture_driver(request: pytest.FixtureRequest) -> Any:
    """The Hamilton driver for the test session.

    This fixture is session-scoped so the driver (and any associated
    compilation work) is shared across all tests in the run.

    Skips the test automatically if no Hamilton modules were configured,
    ensuring that projects without Hamilton are never affected.
    """
    plugin: _HamiltonPlugin | None = request.config.pluginmanager.get_plugin(_PLUGIN_NAME)
    if plugin is None:
        pytest.skip(
            "No Hamilton modules configured. "
            "Set 'hamilton_modules' in pytest.ini / pyproject.toml "
            "or pass --hamilton-modules on the command line."
        )
    return plugin.driver


@pytest.fixture
def input_config(request: pytest.FixtureRequest) -> dict[str, Any]:
    """Input values for the Hamilton DAG, loaded from a JSON file.

    The JSON file is specified via --hamilton-config on the CLI or via
    the 'hamilton_config' ini option.  Returns an empty dict when neither
    is set, which is valid for DAGs whose inputs are fully defaulted.

    Override this fixture in your own conftest.py to supply inputs
    programmatically — for example, by reading from a database fixture or
    by constructing values dynamically per test.

    Example override::

        # conftest.py
        import pytest

        @pytest.fixture
        def input_config(db_connection):
            return {"features": db_connection.fetch("SELECT ...")}
    """
    config_path = _get_hamilton_option(request.config, "config")
    if not config_path:
        return {}
    return json.loads(Path(config_path).read_text())


@pytest.fixture
def hamilton_fixtures(
    request: pytest.FixtureRequest,
    hamilton_fixture_driver: Any,
    input_config: dict[str, Any],
) -> dict[str, Any]:
    """Execute the Hamilton DAG for the subset of nodes requested by this test.

    Only nodes whose names appear in ``request.fixturenames`` are computed,
    so each test pays only for the DAG work it actually needs.  The result
    is a plain ``dict`` mapping node name to computed value.

    Downstream per-node fixtures (e.g. ``add``, ``multiply``) pull their
    values from this dict, so they are all computed in a single
    ``driver.execute()`` call rather than one call per fixture.
    """
    available = {node.name for node in hamilton_fixture_driver.list_available_variables()}
    requested = set(request.fixturenames)
    to_compute = list(available & requested)

    logger.info("hamilton_fixtures: computing nodes %s", to_compute)
    return hamilton_fixture_driver.execute(final_vars=to_compute, inputs=input_config)
