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
