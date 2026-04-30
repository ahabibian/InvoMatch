# EPIC 28 — Security Hardening & Trust Boundary Enforcement

## Status

Implemented.

EPIC 28 hardens the existing authentication, authorization, tenant, and audit boundaries.

## Baseline Before EPIC 28

Before this EPIC, the system already had:

- authentication boundary
- role and permission model
- authorization service
- tenant-scoped run operations
- tenant-aware finalized projection layer
- persistent security audit events
- permission boundary scenario coverage

However, token lifecycle behavior was incomplete.

Static tokens resolved directly to principals and did not enforce:

- token expiry
- token revocation
- lifecycle-specific authentication failure reasons

## Security Hardening Implemented

### 1. Token Lifecycle Management

`StaticTokenProvider` now loads structured token records instead of only token-to-principal mappings.

Each token record supports:

- `token`
- `principal`
- `expires_at`
- `revoked`

Expired tokens are rejected deterministically.

Revoked tokens are rejected deterministically.

### 2. Authentication Lifecycle Enforcement

`AuthenticationService` now validates token lifecycle state before returning an authenticated principal.

Failure reasons now include:

- `missing_authorization_header`
- `malformed_authorization_header`
- `empty_bearer_token`
- `unknown_token`
- `token_expired`
- `token_revoked`

### 3. Deterministic Failure Responses

The API security dependency now maps lifecycle failures to deterministic responses:

- expired token -> HTTP 401, `Token expired`
- revoked token -> HTTP 401, `Token revoked`
- missing/malformed/unknown token -> HTTP 401, `Authentication required`

Permission failures remain HTTP 403.

### 4. Authorization Enforcement

Centralized authorization remains enforced through:

- `AuthorizationService`
- `ROLE_PERMISSIONS`
- `require_permission`

### 5. Tenant Boundary Enforcement

Scenario 11 verifies that tenant B cannot observe tenant A run data through the run listing endpoint.

### 6. Sensitive Action Audit

Privileged actions continue to record `privileged_action_executed` events through the security audit service.

### 7. Security Audit Coverage

Scenario 11 verifies persisted audit coverage for:

- missing authentication
- expired token
- revoked token
- authorization denied
- privileged action execution

Security-boundary failures without a principal are stored under the `security-boundary` tenant.

Tenant-associated security events are stored under the principal tenant.

## New Scenario

### Scenario 11 — Security Boundary Enforcement

Implemented in:

- `tests/system/test_security_boundary_enforcement.py`

Validated flows:

- request without token is rejected
- expired token is rejected
- revoked token is rejected
- viewer cannot execute protected action
- operator can submit input
- tenant B cannot see tenant A run list data
- admin can query audit events
- viewer cannot query audit events
- security audit events are persisted with expected event types and reasons

## Regression Scenario Re-runs

EPIC 28 requires the following scenario coverage:

- Scenario 1 — Happy Path Full Flow
- Scenario 2 — Review Resolution Flow
- Scenario 4 — Runtime Failure Terminalization
- Scenario 7 — Startup Repair Visibility & Recovery Alignment
- Scenario 8 — Permission Boundary Enforcement
- Scenario 9 — Audit Persistence Integrity
- Scenario 10 — Tenant Isolation Integrity
- Scenario 11 — Security Boundary Enforcement

Executed command:

~~~powershell
pytest -q `
  tests\system\test_happy_path_full_flow.py `
  tests\system\test_review_resolution_flow.py `
  tests\runtime\test_runtime_failure.py `
  tests\system\test_startup_repair_visibility_recovery_alignment.py `
  tests\system\test_permission_boundary_enforcement.py `
  tests\audit\test_scenario_9_audit_persistence_integrity.py `
  tests\test_run_store_tenant_isolation.py `
  tests\system\test_security_boundary_enforcement.py `
  --basetemp=.pytest_tmp
~~~

Result:

~~~text
16 passed in 3.99s
~~~

## Focused Security Regression

Executed command:

~~~powershell
pytest -q `
  tests\system\test_security_boundary_enforcement.py `
  tests\system\test_permission_boundary_enforcement.py `
  tests\audit\test_security_audit_persistence.py `
  tests\audit\test_audit_api.py `
  tests\audit\test_scenario_9_audit_persistence_integrity.py `
  tests\helpers\security.py `
  --basetemp=.pytest_tmp
~~~

Result:

~~~text
6 passed in 4.02s
~~~

## Files Changed

- `src/invomatch/services/security/token_provider.py`
- `src/invomatch/services/security/authentication_service.py`
- `src/invomatch/api/security/dependencies.py`
- `tests/system/test_security_boundary_enforcement.py`
- `docs/architecture/EPIC_28_SECURITY_HARDENING.md`

## Closure Criteria

EPIC 28 is closed when:

- token lifecycle is enforced
- expired tokens are rejected
- revoked tokens are rejected
- authentication failures are deterministic
- permission failures remain deterministic
- tenant isolation is preserved
- privileged actions remain guarded
- security audit events are persisted
- Scenario 11 passes
- required regression scenarios remain green

Current status:

- Scenario 11: passing
- Focused security regression: passing
- Required EPIC 28 scenario regression: passing

## Non-Goals Confirmed

This EPIC does not implement:

- OAuth
- SSO
- MFA
- external identity providers
- advanced RBAC hierarchy
- compliance certification
- encryption-at-rest redesign
- infrastructure-level security

## Key Principle

Security is not a feature.

It is the guarantee that system boundaries cannot be bypassed.