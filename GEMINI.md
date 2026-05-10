# GEMINI.md

This file provides context and instructions for the `pytest-hamilton` project, a `pytest` plugin for [Apache Hamilton](https://github.com/apache/hamilton).

## Project Overview

`pytest-hamilton` automatically transforms nodes in a Hamilton DAG into ready-to-use `pytest` fixtures. It aims to eliminate boilerplate by allowing tests to request any computed node by name, with the plugin handling DAG execution and input management.

### Core Technologies
- **Python 3.10–3.14**
- **pytest**: The testing framework and plugin host.
- **sf-hamilton**: The underlying DAG orchestration library.
- **uv**: Dependency management and project isolation.
- **just**: Command runner for development tasks.
- **ruff**: Linting and formatting.
- **ty**: Static type checking.
- **nox**: Matrix testing (run via `uvx`).

### Architecture
- **Plugin Entry Point**: Defined in `pyproject.toml` via `[project.entry-points.pytest11]`.
- **Dynamic Fixture Registration**:
    - `pytest_addoption`: Registers CLI flags (`--hamilton-modules`, `--hamilton-config`) and `ini` options.
    - `pytest_configure`: Scans configured Hamilton modules, builds a `hamilton.driver.Driver`, and dynamically attaches fixture functions to the `pytest_hamilton.pytest_hamilton` module.
    - `pytest_unconfigure`: Safely removes dynamic fixtures and cleans up `sys.path` mutations.
- **Key Fixtures**:
    - `hamilton_fixture_driver` (session): The core Hamilton driver.
    - `input_config` (function): Loads input values from JSON or a `conftest.py` override.
    - `hamilton_fixtures` (function): Coordinates the execution of requested DAG nodes.

## Building and Running

The project uses `uv` for environment management. `just` is the primary command runner for single-Python tasks (defaulting to 3.14), while `nox` handles the cross-version matrix.

### Development Commands
| Task | Command |
|------|---------|
| **Install Deps** | `uv sync --extra test` |
| **Run All QA** | `just qa` (Format, lint, type-check, test on 3.14) |
| **Run Tests** | `just test` (Scoped to `tests/` directory) |
| **Test All Pythons** | `just testall` (3.10 through 3.14 via `nox`) |
| **Test Examples** | `just examples` (Tests standalone templates via `nox`) |
| **Type Check** | `uv run ty check .` (Excludes `examples/`, `.nox/`, `noxfile.py`) |
| **Lint/Format** | `uv run ruff check .` / `uv run ruff format .` (Excludes `examples/`, `.nox/`) |
| **Build Package** | `just build` |

## Development Conventions

### Coding Style
- **Formatting**: Managed by `ruff`. Line length is set to **120**.
- **Linting**: Rules `E`, `W`, `F`, `I`, `B`, and `UP` are enforced. `examples/` are excluded from root linting.
- **Types**: Mandatory type hints, checked via `ty`. All rules are treated as errors.

### Testing Practices
- **Isolation**: Tests use the `pytester` fixture to run `pytest` in a subprocess (`runpytest_subprocess`). This ensures the plugin loading and configuration are verified in a clean environment.
- **Coverage**: Branch coverage is enabled for `src/pytest_hamilton`. Note that `runpytest_subprocess` bypasses standard coverage collection; the reported coverage (~36%) is lower than actual execution.
- **Dynamic DAGs**: Test cases typically use `pytester.makepyfile` to create temporary Hamilton modules and verify fixture injection.
- **Location**: All core plugin tests reside in the `tests/` directory.

### Project Structure
- `src/pytest_hamilton/`: Main package logic.
    - `pytest_hamilton.py`: Plugin implementation (single module).
- `tests/`: Integration tests using `pytester`.
- `examples/`: Standalone project templates with their own `pyproject.toml`.
- `plans/`: Architectural designs and research material.
- `noxfile.py`: Matrix test definitions (Python 3.10–3.14).
