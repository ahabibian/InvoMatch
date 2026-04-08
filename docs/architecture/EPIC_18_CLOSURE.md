# EPIC 18 - Closure
## Operational Reliability / Runtime Hardening

## 1. Closure Decision

EPIC 18 is closed for the implemented runtime hardening scope.

The system now behaves as a deterministic, failure-aware runtime surface across:

- runtime failure normalization
- retry / terminalization policy
- stuck-run assessment
- recovery scan baseline
- lease-safe re-entry claim handoff
- structured terminal run error persistence
- run view failure propagation
- degraded run view projection behavior

This EPIC hardens runtime trustworthiness.
It does not introduce new product flow scope.

---

## 2. Delivered Scope

### Runtime Failure Model
Implemented canonical runtime failure categories and structured runtime failure records.

Delivered categories:

- `execution_failure`
- `orchestration_failure`
- `dependency_failure`
- `persistence_failure`
- `retry_exhausted`
- `unexpected_internal_error`

### Retry / Terminalization
Implemented deterministic retry policy and terminalization behavior through the runtime executor.

Delivered rules:

- no hidden retry
- retryability is policy-driven
- retry exhaustion terminalizes deterministically
- terminal failures persist explicit failed run state

### Stuck Run Handling
Implemented stuck-run assessment baseline for processing runs.

Delivered decisions:

- `none`
- `reenter`
- `fail`

### Recovery Scan
Implemented deterministic recovery scanning for stuck processing runs.

Delivered behavior:

- healthy processing runs remain unchanged
- re-enterable stuck runs surface as re-entry candidates
- unrecoverable stuck runs are terminalized safely

### Lease / Concurrency Integrity
Implemented lease-safe re-entry claim handoff through the canonical claim path.

Delivered guarantees:

- expired-lease recovery claim uses deterministic time injection
- re-entry claim preserves canonical run ownership semantics
- non-eligible runs are rejected
- non-reenterable runs are rejected

### Structured Terminal Failure Surface
Implemented structured `RunError` persistence on failed runs.

Delivered behavior:

- failed runs store structured error metadata
- legacy `error_message` remains for bounded backward compatibility
- failed execution does not falsely present completed state

### Product-safe Failure Propagation
Implemented structured failure propagation into the run view contract.

Delivered run view error fields:

- `code`
- `message`
- `retryable`
- `terminal`

### Degraded Read Safety
Implemented bounded degradation behavior for run view dependencies.

Delivered fallback rules:

- artifact dependency failure -> empty artifact list
- review dependency failure -> `not_started` review summary
- export readiness evaluator failure -> export readiness degrades to `False`
- failed run structured error remains visible under dependency degradation

---

## 3. Key Files Added or Updated

### Runtime
- `src/invomatch/runtime/runtime_failure.py`
- `src/invomatch/runtime/runtime_policy.py`
- `src/invomatch/runtime/runtime_executor.py`
- `src/invomatch/runtime/stuck_run.py`

### Services
- `src/invomatch/services/reconciliation.py`
- `src/invomatch/services/reconciliation_runs.py`
- `src/invomatch/services/runtime_recovery_service.py`
- `src/invomatch/services/run_view_query_service.py`

### Domain / Product Models
- `src/invomatch/domain/models.py`
- `src/invomatch/api/product_models/run_view.py`

### Tests
- `tests/runtime/test_runtime_failure.py`
- `tests/runtime/test_runtime_policy.py`
- `tests/runtime/test_runtime_executor.py`
- `tests/runtime/test_stuck_run.py`
- `tests/runtime/test_recovery_service.py`
- `tests/runtime/test_recovery_reentry_claim.py`
- `tests/test_reconciliation_service.py`
- `tests/test_reconciliation_runs.py`
- `tests/test_run_view_query_service.py`
- `tests/test_run_view_contract.py`
- `tests/test_run_view_api.py`
- `tests/test_run_view_dependency_degradation.py`
- `tests/test_run_view_projection_resilience.py`

### Architecture
- `docs/architecture/EPIC_18_RUNTIME_HARDENING.md`

---

## 4. Verification Evidence

The final EPIC 18 verification set passed with:

- `92 passed`

Validated coverage includes:

- runtime failure classification
- retry policy behavior
- executor terminalization
- stuck-run assessment
- recovery scan
- re-entry claim behavior
- reconciliation failure persistence
- structured run error persistence
- structured run view error propagation
- degraded run view dependency behavior

---

## 5. What This EPIC Explicitly Does Not Do

The following items are intentionally deferred and are not required for EPIC 18 closure:

- automatic execution resume after recovery claim
- background recovery worker loop
- full runtime audit/event history persistence
- broad structured error rollout across every API endpoint
- deployment/infrastructure observability rollout

These belong to later operationalization work, not this EPIC.

---

## 6. Final Assessment

Before EPIC 18:
- the system could execute the happy path
- runtime failure behavior was not fully structured
- recovery and degraded read behavior were not fully bounded

After EPIC 18:
- runtime failure behavior is canonical and deterministic
- terminal failure state is explicit and structured
- stuck processing runs can be assessed and handled safely
- re-entry claim is lease-safe
- product-facing run view preserves failure truth
- degraded run view dependencies fail safely instead of silently fabricating healthy state

EPIC 18 is therefore closed for its intended runtime hardening scope.