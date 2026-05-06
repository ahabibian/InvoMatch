# Mini-EPIC 32.0 Closure - Release Pipeline Baseline & Validation Contract

## Status

Closed.

## Summary

Mini-EPIC 32.0 established the EPIC 32 release validation baseline.

The work created the release pipeline architecture document and repaired legacy test drift caused by finalized projection invariants.

Created:

- docs/architecture/EPIC_32_RELEASE_PIPELINE.md
- docs/architecture/MINI_EPIC_32_0_CLOSURE.md

## Important Finding

The first full backend baseline exposed release-blocking test drift:

8 failed, 680 passed

The failures were caused by old tests creating or reading completed runs without finalized projection stores or readable finalized projections.

This violated the current invariant:

A completed run must have a finalized projection that can be read back safely.

The tests were repaired without weakening production behavior.

## Updated Test Files

- tests/services/test_reconciliation_match_persistence.py
- tests/system/test_review_required_taxonomy_alignment.py
- tests/test_end_to_end_run_flow.py
- tests/test_restart_app_review_run_view_integrity.py
- tests/test_restart_consistency_repair.py
- tests/test_restart_run_view_consistency.py
- tests/test_review_resolution_coordinator.py
- tests/test_run_view_dependency_degradation.py

## Validation Evidence

Required scenario regression pack:

29 passed in 35.08s

Operational validation pack:

78 passed in 31.59s

Contract validation pack:

10 passed in 2.32s

Full backend validation pack:

688 passed in 80.55s

Frontend lint:

eslint completed with no reported errors.

Frontend build:

tsc -b and vite build completed successfully.
Vite transformed 28 modules.
Built in 549ms.

## Scenario Mapping

Scenario 1 - Happy Path Full Flow:
tests/system/test_happy_path_full_flow.py

Scenario 4 - Runtime Failure Terminalization:
tests/system/test_runtime_failure_terminalization.py

Scenario 6 - Restart Recovery Consistency:
tests/system/test_restart_recovery_consistency.py

Scenario 7 - Startup Repair Visibility & Recovery Alignment:
tests/system/test_startup_repair_visibility_recovery_alignment.py

Scenario 13 - Monitoring & Health Visibility Integrity:
tests/test_health.py
tests/test_health_readiness.py
tests/operational/test_operations_metrics_api.py
tests/operational

## Release Contract Established

The following validation layers are now release-blocking:

- required scenario regression pack
- operational validation pack
- contract validation pack
- full backend validation pack
- frontend lint
- frontend build

## Known Limitation

Backend dependencies are not yet fully reproducible because pyproject.toml uses unpinned dependencies.

This is documented in EPIC_32_RELEASE_PIPELINE.md and must be solved in later EPIC 32 work.

## Out of Scope

Mini-EPIC 32.0 did not implement CI, deployment automation, rollback automation, Docker changes, Kubernetes, infrastructure-as-code, or cloud deployment.

That was intentional.

## Closure Result

Mini-EPIC 32.0 is closed.

The next step should be CI automation of this exact validation contract.