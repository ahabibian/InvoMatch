# EPIC 15 — Closure
# Product Flow / Run-to-Outcome Experience

---

## 1. Closure Summary

EPIC 15 focused on hardening InvoMatch as a coherent product experience from the user perspective.

The goal was not UI delivery, but deterministic product behavior across the full run-to-outcome flow.

This EPIC is considered closed for the currently implemented product action set.

---
## 2.1 Central Action Guard

A central action guard was introduced to define and enforce product-visible action availability by run state.

Implemented file:
- src/invomatch/services/actions/action_guard.py

Implemented product state/action matrix:

- queued → no actions
- processing → no actions
- review_required → resolve_review
- completed → export_run
- failed → no actions
- cancelled → no actions

This matrix reflects the currently implemented product actions, not future planned actions.

---
## 2.2 Action Service Enforcement

ActionService was hardened to enforce action/state compatibility before dispatch.

Implemented file:
- src/invomatch/services/action_service.py

Behavior introduced:
- unsupported actions are rejected deterministically
- invalid action/state combinations return conflict
- missing runs return not_found
- invalid handler payloads return invalid_request
- execution failures remain failed

Guard enforcement is currently run_store-aware.

---
## 2.3 API Behavior Hardening

The reconciliation actions API was updated to:
- resolve dependencies from application state
- preserve injected action service seams for tests
- map internal action results to stable HTTP semantics

Implemented file:
- src/invomatch/api/actions.py

HTTP mapping:

- accepted → 200
- invalid_request → 400
- unsupported_action → 400
- conflict → 409
- not_found → 404
- failed → 500

---
## 2.4 End-to-End Product Flow Validation

An end-to-end product flow test suite was added.

Implemented file:
- tests/test_product_flow_end_to_end.py

Validated behavior:

- review_required allows resolve_review
- review_required rejects export_run
- completed allows export_run
- completed rejects resolve_review

---
## 3. Test Evidence

Executed test suites:

- test_product_flow_end_to_end
- test_action_guard
- test_actions
- test_actions_api
- test_product_contract_actions
- test_run_view_api
- test_run_view_contract
- test_export_api

Result:

50 passed in 2.37s

---
## 4. Product Impact

System behavior is now predictable and consistent from a user perspective.

- action availability is explicit
- invalid actions are rejected deterministically
- API semantics are stable

---

## 5. Limitations

Not yet implemented:

- cancel
- retry_run
- inspect
- bulk_resolve

Guard reflects implemented actions only.

---

## 6. Closure Decision

EPIC 15 is closed for the implemented product flow scope.

All flows are enforced, test-covered, and API-aligned.

---
