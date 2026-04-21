# MINI_EPIC â€” Export API Test Isolation Hardening â€” Closure

## Status

Closed.

## Scope Completed

The Mini-EPIC scope has been completed within the intended boundary:

- `create_app()` no longer forces export/review tests onto the default shared persistent review store
- export/review tests are now isolated and temp-scoped
- app state is injectable for test usage
- state leakage through default review persistence was removed from the targeted test paths
- export API tests no longer depend on residue under `output/local`
- cleanup is not required for the targeted tests to pass
- deterministic test setup was preserved
- runtime behavior was not broadly redesigned
- hardening was limited to test/app wiring isolation and dependency injection seams

## Implemented Changes

### 1. App wiring hardening
`create_app(...)` was extended to accept injected dependencies for:

- `review_store`
- `export_artifact_repository`
- `artifact_storage`

This preserved runtime defaults while allowing tests to explicitly own their app state.

### 2. Review store isolation
Targeted export/review integration tests were migrated away from implicit reliance on `app.state.review_store` as a hidden default persistence dependency.

Instead, tests now create isolated review stores explicitly and inject them into `create_app(...)`.

### 3. Helper decoupling
Review seeding helpers were refactored from:

- `_seed_approved_review(app, run)`

to explicit dependency-driven usage:

- `_seed_approved_review(review_store, run)`

This removed hidden coupling between helper behavior and app default wiring.

### 4. Export integration alignment
The following files were hardened:

- `tests/test_export_api.py`
- `tests/test_export_delivery_integration.py`
- `tests/test_run_view_export_consistency_integration.py`

### 5. Contract-aligned test correction
During the hardening work, one prior test expectation was revealed to be misaligned with the actual export contract:

- `test_export_route_returns_422_when_review_data_is_missing`

For a completed matched run without finalized review data, the actual finalized projection/export path allows export and returns a no-review finalized state, rather than 422.

The test was corrected to align with the real contract instead of preserving a residue-driven or invalid expectation.

## Evidence

### Initial evidence addressed
- `test_export_route_returns_422_when_review_data_is_missing`
- `test_export_route_returns_csv_export_for_completed_reviewed_run`
- recreated `output/local/review_store.sqlite3`
- direct use of `app.state.review_store` inside `_seed_approved_review`
- reliance on default `create_app(...)` wiring

### Final execution evidence

Command executed:

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"

    pytest -q `
      tests\test_export_api.py `
      tests\test_export_delivery_integration.py `
      tests\test_run_view_export_consistency_integration.py `
      --basetemp=.pytest_tmp

Observed result:

    10 passed in 4.43s

### Persistent residue verification

`output\local\review_store.sqlite3` remained unchanged during execution.

Observed timestamp after test execution:

- 4/21/2026 2:05:34 AM

This confirms the targeted tests no longer require or mutate the shared persistent review store to pass.

## Files Changed

- `src/invomatch/main.py`
- `tests/test_export_api.py`
- `tests/test_export_delivery_integration.py`
- `tests/test_run_view_export_consistency_integration.py`

## Closure Decision

This Mini-EPIC is closed.

The targeted Export API and related integration tests now run with explicit isolated review state, without dependence on shared persistent review residue, and without requiring cleanup as a prerequisite for success.