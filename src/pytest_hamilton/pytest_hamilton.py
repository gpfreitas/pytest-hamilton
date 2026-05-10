"""pytest-hamilton: automatic Hamilton-based fixtures for pytest."""

from __future__ import annotations

import importlib
import json
import logging
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

logger = logging.getLogger(__name__)

_PLUGIN_NAME = "hamilton_driver_plugin"
_NODES_PLUGIN_NAME = "hamilton_nodes_plugin"

# Names that must never be shadowed by dynamically-registered node fixtures.
_RESERVED_FIXTURE_NAMES: frozenset[str] = frozenset(
    {
        # Plugin's own fixtures
        "hamilton_fixture_driver",
        "hamilton_fixtures",
        "input_config",
        # pytest built-in fixtures
        "request",
        "tmp_path",
        "tmp_path_factory",
        "capsys",
        "capfd",
        "caplog",
        "monkeypatch",
        "pytester",
        "recwarn",
        "doctest_namespace",
        "cache",
        "record_property",
        "record_testsuite_property",
        "record_xml_attribute",
        "pytestconfig",
    }
)


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
    if cli_val is not None:
        return cli_val
    ini_val: str = config.getini(f"hamilton_{name}")
    return ini_val if ini_val else None


# ---------------------------------------------------------------------------
# Plugin class: carries the Hamilton driver
# ---------------------------------------------------------------------------


class _HamiltonDriverPlugin:
    """Holds the Hamilton driver so fixtures can retrieve it via the plugin manager."""

    def __init__(self, driver: Any) -> None:
        self.driver = driver


# ---------------------------------------------------------------------------
# Dynamic fixture factory
# ---------------------------------------------------------------------------


def _make_node_fixture(name: str) -> Callable[..., Any]:
    """Return a function-scoped pytest fixture that extracts *name* from hamilton_fixtures."""

    @pytest.fixture(name=name)
    def _node_fixture(self: Any, hamilton_fixtures: dict[str, Any]) -> Any:
        return hamilton_fixtures[name]

    return _node_fixture


# ---------------------------------------------------------------------------
# Plugin configuration: build the driver and register fixtures
# ---------------------------------------------------------------------------


_stash_key = pytest.StashKey[dict[str, Any]]()


def pytest_configure(config: pytest.Config) -> None:
    """Build the Hamilton driver and register one fixture per DAG node.

    This hook runs before collection, so any fixture functions added here to
    the plugin module will be discovered when pytest scans the module later.
    If no modules are configured the plugin is a complete no-op and never
    interferes with existing test suites.
    """
    modules_spec = _get_hamilton_option(config, "modules")
    if not modules_spec:
        return

    # Prepend rootdir to sys.path so that module names relative to the project
    # root (or pytester sandbox) are importable at configure time, before
    # pytest's own import machinery adds them during collection.
    rootdir = str(config.rootpath)
    added_to_sys_path = False
    if rootdir not in sys.path:
        sys.path.insert(0, rootdir)
        added_to_sys_path = True

    import hamilton.driver  # imported lazily; sf-hamilton is a runtime dep

    module_names = [m.strip() for m in modules_spec.split(",") if m.strip()]

    modules = []
    for name in module_names:
        try:
            modules.append(importlib.import_module(name))
        except ModuleNotFoundError as exc:
            hint = ""
            if name.endswith(".py"):
                hint = f" Did you mean {name[:-3]!r}? (Remove the .py extension)"
            raise pytest.UsageError(
                f"pytest-hamilton: could not import module {name!r}.{hint} "
                "Check the --hamilton-modules flag or 'hamilton_modules' ini option."
            ) from exc

    try:
        driver = hamilton.driver.Builder().with_config({}).with_modules(*modules).build()
    except Exception as exc:
        # Hamilton's Builder surfaces graph-construction errors as a mix of
        # ValueError, KeyError, and lifecycle ValidationException with no
        # common public base. Catch broadly and re-wrap as UsageError.
        raise pytest.UsageError(
            f"pytest-hamilton: failed to build the Hamilton driver from modules {module_names!r}: {exc}"
        ) from exc

    # Register the driver carrier so hamilton_fixture_driver can retrieve it.
    config.pluginmanager.register(_HamiltonDriverPlugin(driver), name=_PLUGIN_NAME)
    logger.info("pytest-hamilton: driver successfully built with modules: %s", module_names)

    # Attach one fixture per DAG node to a dedicated plugin object and register
    # it. Registering a new plugin object here (during configure) ensures that
    # pytest's FixtureManager scans it and discovers the dynamic fixtures,
    # even if the main plugin module was already scanned during initial
    # registration.
    fixture_map = {}
    registered_node_names: list[str] = []
    for node in driver.list_available_variables():
        if node.name in _RESERVED_FIXTURE_NAMES:
            logger.warning(
                "pytest-hamilton: skipping Hamilton node %r because it would "
                "shadow a built-in or plugin fixture with the same name.",
                node.name,
            )
            continue
        fixture_map[node.name] = _make_node_fixture(node.name)
        registered_node_names.append(node.name)

    DynamicNodesPlugin = type("_HamiltonDynamicNodesPlugin", (), fixture_map)
    config.pluginmanager.register(DynamicNodesPlugin(), name=_NODES_PLUGIN_NAME)

    # Stash cleanup info so pytest_unconfigure can reverse the mutations.
    config.stash[_stash_key] = {
        "registered_node_names": registered_node_names,
        "added_to_sys_path": rootdir if added_to_sys_path else None,
    }


def pytest_unconfigure(config: pytest.Config) -> None:
    """Clean up mutations made during pytest_configure."""
    cleanup = config.stash.get(_stash_key, None)
    if cleanup is None:
        return

    rootdir = cleanup["added_to_sys_path"]
    if rootdir and rootdir in sys.path:
        sys.path.remove(rootdir)

    if config.pluginmanager.get_plugin(_NODES_PLUGIN_NAME) is not None:
        config.pluginmanager.unregister(name=_NODES_PLUGIN_NAME)

    if config.pluginmanager.get_plugin(_PLUGIN_NAME) is not None:
        config.pluginmanager.unregister(name=_PLUGIN_NAME)


# ---------------------------------------------------------------------------
# Public fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def hamilton_fixture_driver(request: pytest.FixtureRequest) -> Any:
    """The Hamilton driver for the test session.

    Session-scoped so the driver and its compilation work are shared across
    all tests.  Skips the test automatically when no Hamilton modules have
    been configured, so projects without Hamilton are never affected.
    """
    plugin: _HamiltonDriverPlugin | None = request.config.pluginmanager.get_plugin(_PLUGIN_NAME)
    if plugin is None:
        pytest.skip(
            "pytest-hamilton: No Hamilton modules configured. "
            "To enable node fixtures, set 'hamilton_modules' in your configuration. "
            "In pytest.ini, use [pytest] section; in pyproject.toml, use [tool.pytest.ini_options] "
            'and ensure strings are quoted (e.g. hamilton_modules = "lib_model"). '
            "Alternatively, pass --hamilton-modules on the command line."
        )
    return plugin.driver


@pytest.fixture
def input_config(request: pytest.FixtureRequest) -> dict[str, Any]:
    """Input values for the Hamilton DAG, loaded from a JSON file.

    Specified via --hamilton-config on the CLI or the 'hamilton_config'
    ini option.  Returns an empty dict when neither is set, which is valid
    for DAGs whose inputs are fully defaulted.

    Override this fixture in your own conftest.py to supply inputs
    programmatically — for example, reading from a database or constructing
    values dynamically per test::

        # conftest.py
        import pytest

        @pytest.fixture
        def input_config(db_connection):
            return {"features": db_connection.fetch("SELECT ...")}
    """
    config_path = _get_hamilton_option(request.config, "config")
    if not config_path:
        return {}
    path = Path(config_path)
    if not path.is_absolute():
        path = request.config.rootpath / path
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def hamilton_fixtures(
    request: pytest.FixtureRequest,
    hamilton_fixture_driver: Any,
    input_config: dict[str, Any],
) -> dict[str, Any]:
    """Execute the Hamilton DAG for only the nodes requested by this test.

    Intersects ``request.fixturenames`` with the set of available DAG nodes,
    then calls ``driver.execute()`` for just that subset.  This means each
    test only pays for the DAG work it actually needs.

    Individual node fixtures (e.g. ``add``, ``multiply``) pull their values
    from this dict, so all requested nodes are computed in one
    ``driver.execute()`` call.
    """
    available = {node.name for node in hamilton_fixture_driver.list_available_variables()}
    requested = set(request.fixturenames)
    to_compute = list(available & requested)

    logger.info("hamilton_fixtures: computing nodes %s", to_compute)
    return hamilton_fixture_driver.execute(final_vars=to_compute, inputs=input_config)
