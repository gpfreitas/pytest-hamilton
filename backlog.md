# Backlog

Open follow-ups not addressed in the current branch. Items here are
intentionally deferred — either out of scope for the work that surfaced
them, or low-priority enough that they don't justify holding up a PR.

## Open

### CI: split lint out of the Python matrix

**Where:** `.github/workflows/test.yml`, `Lint with ruff` step (currently
runs once per Python version in the matrix).

**Problem:** Ruff output is deterministic across Python versions, so
running the lint step five times (3.10–3.14) wastes ~80% of its CI
minutes for no additional signal.

**Fix sketch:** Extract lint into a separate non-matrix job that runs
once on a single Python version. Keep `Run plugin tests (nox)` and
`Run example templates (nox)` matrix-driven.

**Why deferred:** Surfaced during a "simplify" pass on unrelated changes
(noxfile + examples). Restructuring CI jobs is a structural change with
its own review surface and was out of scope for that pass.

### Plugin: expose Hamilton build-time config (`@config.when` support)

**Where:** `src/pytest_hamilton/pytest_hamilton.py`, the `Builder()
.with_config({}).with_modules(*modules).build()` call inside
`pytest_configure`.

**Problem:** The Builder's `with_config(...)` argument is hardcoded to
`{}`, so users of Hamilton's `@config.when` / `@config.when_in`
decorators have no way to feed build-time configuration into the DAG.
Today the only escape valve is to pre-construct a Driver in a custom
conftest, which defeats the plugin's auto-fixture story.

**Fix sketch:** Add a third option pair (CLI flag + ini key, e.g.
`--hamilton-build-config` / `hamilton_build_config`) accepting either a
JSON file path or inline JSON; thread it into the Builder's
`with_config(...)` call. Keep the existing `--hamilton-config` /
`hamilton_config` (which feeds `driver.execute(inputs=...)`) untouched —
they serve different purposes (build-time vs run-time inputs). Add a
test that uses a `@config.when`-decorated function and verifies the
right branch is selected per build-config value.

**Why deferred:** Real feature work — needs option naming, docs, an
example in `examples/`, and a fresh test. No user has reported the
limitation yet; folding it into a review-driven cleanup pass would
inflate scope.

### Coverage: subprocess pytester runs aren't measured

**Where:** `tests/test_pytest_hamilton.py` (whole suite uses
`pytester.runpytest_subprocess(...)`), `pyproject.toml`
`[tool.coverage.run]`.

**Problem:** The plugin's tests intentionally spawn a fresh pytest
process per case via `runpytest_subprocess` so the plugin loads from a
clean state with no shared fixtures or import caches. But `coverage
run` only instruments the parent process, so all the plugin code that
actually executes inside the child pytest is invisible to the report.
After scoping coverage to `src/pytest_hamilton/` (commit `6c75a2f`),
the report shows ~36% — far below the real coverage the suite
exercises.

**Fix sketch:** wire up subprocess coverage. Two parts:

1. Add `[tool.coverage.run].parallel = true` and a `sitecustomize.py`
   (or set `COVERAGE_PROCESS_START=pyproject.toml`) so child processes
   that import the package start their own coverage context. See
   <https://coverage.readthedocs.io/en/latest/subprocess.html>.
2. Run `coverage combine` before `coverage report`/`html` in the
   justfile target, to merge the parent's `.coverage` with each child's
   `.coverage.<pid>` file.

Alternatively (smaller change), switch select tests that don't need a
fully fresh interpreter to `pytester.runpytest(...)` (in-process) so
they're measured directly. This sacrifices some isolation, so
`runpytest_subprocess` should remain the default for tests that
specifically care about plugin load order.

**Why deferred:** The 36% number is misleading but not wrong — it
reflects the parent process only, and the suite itself has solid
functional coverage as written. Wiring up subprocess coverage is its
own small project (config + justfile + verifying numbers look right)
and not what the recent coverage-config commit was scoped to.
