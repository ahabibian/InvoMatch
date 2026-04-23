# EPIC 25 Test Strategy

## Purpose

Define the validation strategy for the authentication and authorization boundary introduced in EPIC 25.

This EPIC is complete only if security policy is not merely documented, but implemented and verified across route protection, backend enforcement, UI alignment, and regression safety.

## Test Strategy Goals

The EPIC 25 test strategy must verify that:

- authentication protects the intended API surface
- authorization rules are enforced consistently
- role boundaries are explicit and predictable
- backend enforcement remains authoritative
- UI permission behavior aligns with backend policy
- security-relevant decisions are auditable
- existing product flow behavior remains stable for authorized users

## Coverage Layers

The validation strategy is divided into:

1. unit tests
2. API / integration tests
3. scenario tests
4. required regression re-runs

## 1. Unit Test Coverage

### Authentication Service Tests

Must verify:

- valid bearer token resolves to authenticated active user
- invalid token is rejected
- unknown token is rejected
- malformed authorization header is rejected
- inactive user is resolved as known identity but blocked correctly

### User / Role / Permission Tests

Must verify:

- role enumeration is stable
- user status handling is explicit
- role-to-capability mapping matches authorization matrix
- default deny behavior applies for unknown capability or unmapped action

### Authorization Service Tests

Must verify:

- viewer allowed capabilities
- operator allowed capabilities
- admin allowed capabilities
- denied capability evaluation returns predictable result
- inactive user cannot pass authorization for protected capability
- action type resolves to the correct required capability

### Security Audit Tests

Must verify:

- authentication failure produces auditable event
- inactive user denial produces auditable event
- authorization denial produces auditable event
- privileged success produces auditable event
- 401 and 403 cases remain distinguishable in audit visibility

## 2. API / Integration Test Coverage

### Public Endpoint Protection Tests

Must verify:

- GET /health remains accessible without authentication
- GET /readiness remains accessible without authentication

### Protected Endpoint Authentication Tests

Must verify protected endpoints reject unauthenticated access with 401:

- POST /api/reconciliation/input/json
- POST /api/reconciliation/input/file
- GET /api/reconciliation/input/{input_id}
- POST /api/reconciliation/runs
- POST /api/reconciliation/runs/ingest
- GET /api/reconciliation/runs
- GET /api/reconciliation/runs/{run_id}
- GET /api/reconciliation/runs/{run_id}/view
- GET /api/reconciliation/runs/{run_id}/review
- POST /api/reconciliation/runs/{run_id}/actions
- GET /api/reconciliation/runs/{run_id}/export
- GET /api/reconciliation/runs/{run_id}/exports
- GET /api/reconciliation/exports/{artifact_id}
- GET /api/reconciliation/exports/{artifact_id}/download

### Role-Based API Authorization Tests

Must verify:

- viewer can access allowed read endpoints
- viewer cannot submit input
- viewer cannot execute run actions
- viewer cannot trigger direct export
- viewer cannot download artifacts in the initial policy

- operator can perform normal product flow endpoints
- operator cannot access admin-only operational capabilities when such routes or service hooks are exposed in tests

- admin can perform all operator product operations
- admin can execute privileged admin-only capabilities when exposed in test surface

### Action Endpoint Integration Tests

Must verify:

- action endpoint protection is not flat
- resolve_review requires actions.resolve_review
- export_run requires actions.export_run
- unsupported action types do not become implicitly authorized
- permission approval does not bypass action_guard lifecycle constraints

### Export Authorization Tests

Must verify:

- direct export endpoint requires export permission
- artifact metadata access is distinct from artifact download
- artifact download obeys artifact download permission
- authorization approval does not bypass export eligibility and artifact availability checks

## 3. Scenario Coverage

### Scenario 8 — Permission Boundary Enforcement

Scenario 8 is mandatory for EPIC 25.

Goal:

Validate that permission boundaries are enforced consistently across authentication, authorization, backend action execution, export access, and UI-aligned behavior.

Scenario 8 must cover at minimum:

#### Case 1: unauthenticated protected access

- protected endpoint request without valid auth
- expected result: 401 Unauthorized
- expected visibility: authentication failure auditable

#### Case 2: inactive user protected access

- valid identity with inactive status attempts protected endpoint
- expected result: 403 Forbidden
- expected visibility: inactive-user denial auditable

#### Case 3: viewer attempts input submission

- viewer attempts JSON or file input submission
- expected result: denied
- expected visibility: authorization denial auditable

#### Case 4: viewer attempts review resolution

- viewer attempts POST /runs/{run_id}/actions with resolve_review
- expected result: denied
- expected visibility: authorization denial auditable

#### Case 5: viewer attempts direct export

- viewer attempts GET /runs/{run_id}/export
- expected result: denied
- expected visibility: authorization denial auditable

#### Case 6: viewer attempts artifact download

- viewer attempts GET /exports/{artifact_id}/download
- expected result: denied
- expected visibility: authorization denial auditable

#### Case 7: operator attempts admin-only capability

- operator attempts reserved admin-only operational capability through test hook or protected service surface
- expected result: denied
- expected visibility: authorization denial auditable

#### Case 8: operator succeeds on normal product action

- operator executes authorized resolve_review or export_run flow
- expected result: allowed when business-state rules also permit
- expected visibility: privileged success auditable

#### Case 9: admin succeeds on privileged capability

- admin executes privileged admin-only capability through test hook or protected surface
- expected result: allowed
- expected visibility: admin usage auditable

#### Case 10: UI / backend alignment proof

- UI-equivalent permission projection indicates hidden or unavailable action
- backend independently denies unauthorized request when attempted anyway
- expected result: UI is aligned but backend remains authoritative

## 4. Required Regression Re-Runs

The following permanent scenarios must be re-run before EPIC 25 closure:

- Scenario 1 — Happy Path Full Flow
- Scenario 2 — Review Resolution Flow
- Scenario 4 — Runtime Failure Terminalization
- Scenario 7 — Startup Repair Visibility & Recovery Alignment

## Regression Intent

### Scenario 1

Confirms that the happy path still works for authorized product users after auth boundary introduction.

### Scenario 2

Confirms review resolution remains correct when authorization checks are added around action execution.

### Scenario 4

Confirms runtime failure and terminalization behavior remain correct and are not broken by auth boundary additions.

### Scenario 7

Confirms startup repair and recovery visibility remain aligned after privileged capability boundaries are introduced.

## Test Data / Fixture Expectations

Validation should include fixture support for at least:

- active viewer
- active operator
- active admin
- inactive user
- invalid token / unknown token request
- representative run in review_required state
- representative run in completed state
- representative export artifact for metadata and download checks

## Default Deny Validation

The tests must explicitly verify that any new or unmapped action type is denied by default.

This protects the generic action endpoint from silent privilege expansion.

## Backend Source-of-Truth Validation

Tests must prove that backend authorization remains authoritative even when UI behavior would normally hide an action.

This means backend denial tests are mandatory even for actions the UI would already hide.

## Closure Evidence Expectations

EPIC 25 test closure must include evidence for:

- auth-protected endpoint behavior
- role-based authorization behavior
- Scenario 8 passing
- required regression scenarios passing
- no product flow regression for authorized operator/admin usage

## Suggested Test Areas

Implementation is expected to add tests in areas such as:

- tests/security/
- tests/test_actions_api.py
- tests/test_export_api.py
- tests/test_export_artifacts_api.py
- tests/test_run_view_api.py
- tests/system/

The exact filenames may follow existing repository conventions, but the coverage obligations defined here are mandatory.

## Closure Rule

EPIC 25 is not complete unless:

- authentication is implemented
- authorization is enforced
- Scenario 8 passes
- required regression scenarios remain green
- audit visibility is verified for key security outcomes