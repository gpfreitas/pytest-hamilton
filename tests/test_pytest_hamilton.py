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

    def test_unconfigured_plugin_fails_on_node_fixture_request(self, pytester):
        """Requesting a node fixture when the plugin is not configured leads to a standard error."""
        pytester.makepyfile("""
            def test_no_config(thesum):
                pass
        """)
        result = pytester.runpytest_subprocess()
        result.assert_outcomes(errors=1)
        result.stdout.fnmatch_lines(["*fixture 'thesum' not found*"])


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

    def test_nested_module_discovery(self, pytester):
        """Hamilton modules in subpackages are discovered correctly."""
        pytester.mkdir("subpackage")
        (pytester.path / "subpackage" / "__init__.py").touch()
        (pytester.path / "subpackage" / "model.py").write_text(_SAMPLE_MODULE_SRC)
        pytester.makefile(".json", input_config=_INPUT_CONFIG_JSON)

        pytester.makepyfile("""
            def test_nested_add(add):
                assert add == 7
        """)
        result = pytester.runpytest_subprocess(
            "--hamilton-modules=subpackage.model",
            "--hamilton-config=input_config.json",
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
        pytester.makefile(".json", alt_config='{"x": 1, "y": 1}')
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
            "--hamilton-config=alt_config.json",
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
        result = pytester.runpytest_subprocess("-rs")
        result.assert_outcomes(skipped=1)
        result.stdout.fnmatch_lines([
            "*SKIPPED*pytest-hamilton: No Hamilton modules configured.*"
        ])


# ---------------------------------------------------------------------------
# TestErrorPaths
# ---------------------------------------------------------------------------


class TestErrorPaths:
    """The plugin reports clear errors on misconfiguration."""

    def test_nonexistent_module_gives_usage_error(self, pytester):
        """--hamilton-modules pointing at a missing module produces a clear error."""
        pytester.makepyfile("""
            def test_placeholder():
                pass
        """)
        result = pytester.runpytest_subprocess(
            "--hamilton-modules=nonexistent_module",
        )
        result.stderr.fnmatch_lines(["*pytest-hamilton: could not import module*"])

    def test_module_name_with_py_extension_gives_hint(self, pytester):
        """Using a .py extension in --hamilton-modules provides a helpful hint."""
        pytester.makepyfile("""
            def test_placeholder():
                pass
        """)
        result = pytester.runpytest_subprocess(
            "--hamilton-modules=lib_model.py",
        )
        result.stderr.fnmatch_lines([
            "*pytest-hamilton: could not import module 'lib_model.py'. Did you mean 'lib_model'? (Remove the .py extension)*"
        ])

    def test_nonexistent_config_file_gives_error(self, pytester):
        """--hamilton-config pointing at a missing file produces an error at test time."""
        pytester.makepyfile(sample_module=_SAMPLE_MODULE_SRC)
        pytester.makepyfile("""
            def test_add(add):
                pass
        """)
        result = pytester.runpytest_subprocess(
            "--hamilton-modules=sample_module",
            "--hamilton-config=nonexistent.json",
        )
        result.assert_outcomes(errors=1)

    def test_malformed_json_config_gives_error(self, pytester):
        """A JSON config file with invalid syntax produces an error at test time."""
        pytester.makepyfile(sample_module=_SAMPLE_MODULE_SRC)
        pytester.makefile(".json", bad_config="{not valid json")
        pytester.makepyfile("""
            def test_add(add):
                pass
        """)
        result = pytester.runpytest_subprocess(
            "--hamilton-modules=sample_module",
            "--hamilton-config=bad_config.json",
        )
        result.assert_outcomes(errors=1)


# ---------------------------------------------------------------------------
# TestFixtureNameCollisions
# ---------------------------------------------------------------------------


class TestFixtureNameCollisions:
    """Nodes whose names collide with reserved fixtures are skipped with a warning."""

    def test_node_shadowing_builtin_is_skipped(self, pytester):
        """A Hamilton node named 'tmp_path' must not shadow pytest's built-in."""
        pytester.makepyfile(
            collision_module="""
def tmp_path(x: int) -> int:
    return x + 1

def safe_node(x: int) -> int:
    return x + 2
"""
        )
        pytester.makefile(".json", input_config='{"x": 5}')
        pytester.makepyfile("""
            import pathlib

            def test_tmp_path_is_still_builtin(tmp_path):
                assert isinstance(tmp_path, pathlib.Path)

            def test_safe_node_works(safe_node):
                assert safe_node == 7
        """)
        result = pytester.runpytest_subprocess(
            "--hamilton-modules=collision_module",
            "--hamilton-config=input_config.json",
        )
        result.assert_outcomes(passed=2)
