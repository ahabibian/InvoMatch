# EPIC 29 — Projection-First Product Model Enforcement & Legacy Report Elimination

## Status

Closed.

## Commit

- Commit: 7c54504
- Message: feat: enforce projection-only run view for completed runs and remove report fallback
- Branch: main
- Pushed to: origin/main

## Goal

Make finalized projection the only product-facing source of truth for completed runs.

## Implemented

- Completed run view now requires finalized projection.
- Missing finalized projection for completed runs fails hard.
- Missing finalized projection store for completed run view fails hard.
- RunView match summary for completed runs reads from finalized projection only.
- Legacy report fallback was removed from completed run view behavior.
- Tests were updated so completed-run product views must provide projection-backed state.
- API and contract tests now reflect projection-first behavior.

## Important Boundary Decision

Low-level reconciliation and projection persistence helpers remain layer-boundary safe.

The hard enforcement is applied at product-facing read/export boundaries, not by breaking all low-level reconciliation paths. This prevents brittle internal flows while still ensuring product behavior is strict and deterministic.

## Validation

Executed regression pack:

- tests/test_run_view_query_service.py
- tests/test_run_view_projection_resilience.py
- tests/test_run_view_contract.py
- tests/test_run_view_api.py
- tests/test_run_view_export_consistency_integration.py
- tests/test_export_readiness_evaluator.py
- tests/test_finalized_projection_store.py
- tests/test_finalized_projection_lifecycle.py
- tests/test_export_api.py
- tests/test_export_delivery_integration.py

Result:

62 passed.

## Exit Criteria

- Completed run view no longer falls back to run.report.
- Completed run without finalized projection fails hard in RunView.
- Product-facing RunView match summary is projection-based.
- Export path remains projection-backed and fails if projection is missing.
- Legacy report is no longer authoritative for completed product views.

## Remaining Risk

Projection generation is still dependent on orchestration wiring. The system now fails safely when projection is missing, but the next step should enforce projection integrity at completion/finalization level.

## Recommended Next EPIC

EPIC 30 — Projection Integrity Enforcement & Completion-Time Guarantee

Goal:
Ensure a run cannot become product-completed unless finalized projection has been created, verified, and persisted.