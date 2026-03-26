"""Tests for pytest-hamilton using pytester.

All tests use ``runpytest_subprocess`` for full isolation: each call spawns a
fresh pytest process, ensuring the plugin is loaded from scratch and that no
in-process state leaks between test cases.

Each test creates a minimal Hamilton module directly in the pytester sandbox
using ``pytester.makepyfile(module_name=...)``, which guarantees the module
is importable by the subprocess without any PYTHONPATH manipulation.
"""

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

#: Source code of the sample Hamilton module used across all tests.
#: Defines a tiny DAG:  x, y → add → add_doubled
#:                       x, y → multiply
_SAMPLE_MODULE_SRC = """
def add(x: int, y: int) -> int:
    return x + y

def multiply(x: int, y: int) -> int:
    return x * y

def add_doubled(add: int) -> int:
    return add * 2
"""

#: JSON content for the default input config (x=3, y=4).
_INPUT_CONFIG_JSON = '{"x": 3, "y": 4}'


def _make_hamilton_env(pytester):
    """Populate the pytester sandbox with sample_module.py and input_config.json.

    Returns the relative path string to the config file so callers can pass
    it directly to --hamilton-config.
    """
    pytester.makepyfile(sample_module=_SAMPLE_MODULE_SRC)
    pytester.makefile(".json", input_config=_INPUT_CONFIG_JSON)
    return "input_config.json"


# ---------------------------------------------------------------------------
# TestHelloWorld
# ---------------------------------------------------------------------------


class TestHelloWorld:
    """The plugin is a transparent no-op when no modules are configured."""

    def test_ordinary_tests_pass_without_hamilton(self, pytester):
        """Projects that don't use Hamilton are completely unaffected."""
        pytester.makepyfile("""
            def test_ordinary():
                assert 1 + 1 == 2
        """)
        result = pytester.runpytest_subprocess()
        result.assert_outcomes(passed=1)


# ---------------------------------------------------------------------------
# TestBasicFixtures
# ---------------------------------------------------------------------------


class TestBasicFixtures:
    """Hamilton DAG nodes become pytest fixtures automatically."""

    def test_add_fixture_returns_sum(self, pytester):
        config = _make_hamilton_env(pytester)
        pytester.makepyfile("""
            def test_add(add):
                assert add == 7  # 3 + 4
        """)
        result = pytester.runpytest_subprocess(
            "--hamilton-modules=sample_module",
            f"--hamilton-config={config}",
        )
        result.assert_outcomes(passed=1)

    def test_multiply_fixture_returns_product(self, pytester):
        config = _make_hamilton_env(pytester)
        pytester.makepyfile("""
            def test_multiply(multiply):
                assert multiply == 12  # 3 * 4
        """)
        result = pytester.runpytest_subprocess(
            "--hamilton-modules=sample_module",
            f"--hamilton-config={config}",
        )
        result.assert_outcomes(passed=1)

    def test_downstream_node_is_computed_correctly(self, pytester):
        """add_doubled depends on add; the DAG should resolve the dependency."""
        config = _make_hamilton_env(pytester)
        pytester.makepyfile("""
            def test_add_doubled(add_doubled):
                assert add_doubled == 14  # (3 + 4) * 2
        """)
        result = pytester.runpytest_subprocess(
            "--hamilton-modules=sample_module",
            f"--hamilton-config={config}",
        )
        result.assert_outcomes(passed=1)

    def test_multiple_fixtures_in_one_test(self, pytester):
        """Multiple Hamilton fixtures can be requested by a single test."""
        config = _make_hamilton_env(pytester)
        pytester.makepyfile("""
            def test_both(add, multiply):
                assert add == 7
                assert multiply == 12
        """)
        result = pytester.runpytest_subprocess(
            "--hamilton-modules=sample_module",
            f"--hamilton-config={config}",
        )
        result.assert_outcomes(passed=1)


# ---------------------------------------------------------------------------
# TestInputConfig
# ---------------------------------------------------------------------------


class TestInputConfig:
    """The input_config fixture loads the JSON file and is overridable."""

    def test_input_config_values_are_loaded(self, pytester):
        config = _make_hamilton_env(pytester)
        pytester.makepyfile("""
            def test_inputs(input_config):
                assert input_config["x"] == 3
                assert input_config["y"] == 4
        """)
        result = pytester.runpytest_subprocess(
            "--hamilton-modules=sample_module",
            f"--hamilton-config={config}",
        )
        result.assert_outcomes(passed=1)

    def test_input_config_is_empty_dict_when_not_specified(self, pytester):
        """input_config returns {} when no config path is provided."""
        pytester.makepyfile(sample_module=_SAMPLE_MODULE_SRC)
        pytester.makepyfile("""
            def test_no_config(input_config):
                assert input_config == {}
        """)
        result = pytester.runpytest_subprocess(
            "--hamilton-modules=sample_module",
            # deliberately omitting --hamilton-config
        )
        result.assert_outcomes(passed=1)

    def test_input_config_can_be_overridden_in_conftest(self, pytester):
        """Users can shadow input_config in their own conftest.py."""
        pytester.makepyfile(sample_module=_SAMPLE_MODULE_SRC)
        pytester.makeconftest("""
            import pytest

            @pytest.fixture
            def input_config():
                return {"x": 10, "y": 20}
        """)
        pytester.makepyfile("""
            def test_add_with_override(add):
                assert add == 30  # 10 + 20
        """)
        result = pytester.runpytest_subprocess(
            "--hamilton-modules=sample_module",
        )
        result.assert_outcomes(passed=1)


# ---------------------------------------------------------------------------
# TestIniOptions
# ---------------------------------------------------------------------------


class TestIniOptions:
    """hamilton_modules and hamilton_config can be set in pytest.ini."""

    def test_ini_option_configures_modules_and_config(self, pytester):
        """Fixtures are created when options are set via ini, no CLI flags needed."""
        config = _make_hamilton_env(pytester)
        pytester.makeini(f"""
            [pytest]
            hamilton_modules = sample_module
            hamilton_config = {config}
        """)
        pytester.makepyfile("""
            def test_add(add):
                assert add == 7
        """)
        result = pytester.runpytest_subprocess()
        result.assert_outcomes(passed=1)

    def test_cli_flag_overrides_ini_config(self, pytester):
        """A --hamilton-config flag overrides the ini value for that run."""
        pytester.makepyfile(sample_module=_SAMPLE_MODULE_SRC)
        pytester.makefile(".json", input_config=_INPUT_CONFIG_JSON)
        alt_config = pytester.makefile(".json", alt_config='{"x": 1, "y": 1}')
        pytester.makeini("""
            [pytest]
            hamilton_modules = sample_module
            hamilton_config = input_config.json
        """)
        pytester.makepyfile("""
            def test_add(add):
                assert add == 2  # 1 + 1 from alt_config, not 3 + 4 from ini
        """)
        result = pytester.runpytest_subprocess(
            f"--hamilton-config={alt_config}",
        )
        result.assert_outcomes(passed=1)


# ---------------------------------------------------------------------------
# TestNoModules
# ---------------------------------------------------------------------------


class TestNoModules:
    """hamilton_fixture_driver skips tests when no modules are configured."""

    def test_hamilton_fixture_driver_skips_without_modules(self, pytester):
        pytester.makepyfile("""
            def test_uses_driver(hamilton_fixture_driver):
                pass  # should be skipped, not failed
        """)
        result = pytester.runpytest_subprocess()
        result.assert_outcomes(skipped=1)
