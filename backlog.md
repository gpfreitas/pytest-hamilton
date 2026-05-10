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
