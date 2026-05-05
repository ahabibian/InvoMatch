# Mini-EPIC 31.6 Closure - Backend Current Session Endpoint Contract

## Status

Closed.

## Context

Mini-EPIC 31.5 documented the frontend auth session context foundation, but the frontend still had no backend endpoint from which it could truthfully derive the authenticated user and permissions.

Before Mini-EPIC 31.6, any frontend role-aware behavior would have risked inventing roles or permissions locally. That would have violated the authentication and authorization boundary established earlier in the product architecture.

Mini-EPIC 31.6 introduced a backend-owned current session contract.

## Goal

Expose a backend-authenticated session endpoint that returns:

- the authenticated principal
- backend-derived permissions
- existing backend 401 behavior for missing, expired, or revoked tokens
- existing backend 403 behavior for inactive users

This endpoint is the contract consumed later by frontend session primitives.

## Confirmed Implementation Commit

- Commit:
  - 8088aaf feat: add backend auth session endpoint
- Branch:
  - main
- Remote:
  - pushed to origin/main

## Implemented Scope

### 1. Backend Auth Session Endpoint

Added endpoint:

- GET /api/auth/session

The endpoint returns the current authenticated principal and the permissions derived from backend role configuration.

### 2. Backend-Derived Permissions

Permissions are derived from the backend permission matrix:

- ROLE_PERMISSIONS
- get_permissions_for_role
- role_has_permission

The frontend is not responsible for calculating or inventing permissions.

### 3. Response Model

The endpoint returns a product-facing session response containing:

- user
- permissions

The user payload includes identity and tenancy fields such as:

- user_id
- username
- role
- status
- tenant_id
- auth_source

### 4. Security Behavior Preserved

The endpoint uses the existing backend authentication behavior.

Preserved behavior:

- missing token returns existing 401 behavior
- expired token returns existing 401 behavior
- revoked token returns existing 401 behavior
- inactive users return existing 403 behavior

No backend security weakening was introduced.

### 5. Role Permission Differences Tested

The session endpoint verifies permission differences across roles.

Confirmed behavior:

- admin includes operations.view_metrics
- viewer does not include operations.view_metrics
- operator does not include operations.view_metrics

This keeps the operational admin boundary backend-owned.

## Files Involved

Primary backend files:

- src/invomatch/api/auth_session.py
- src/invomatch/api/product_models/auth_session.py
- src/invomatch/services/security/permission_matrix.py
- src/invomatch/domain/security/permission.py

Validation file:

- tests/test_auth_session_api.py

## Explicit Non-Goals Preserved

This Mini-EPIC did not add:

- frontend login
- frontend logout
- OAuth/OIDC
- SSO
- refresh token logic
- frontend role calculation
- frontend permission calculation
- new operational permissions
- changes to operational endpoint behavior
- weakening of existing backend auth behavior

## Validation Evidence

### Backend Auth Session Tests

Command:

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"
    pytest -q tests\test_auth_session_api.py --basetemp=.pytest_tmp

Result:

    6 passed

### Backend/System Validation Pack

Command:

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"

    pytest -q `
      tests\system\test_happy_path_full_flow.py `
      tests\system\test_review_resolution_flow.py `
      tests\system\test_runtime_failure_terminalization.py `
      tests\system\test_startup_repair_visibility_recovery_alignment.py `
      tests\operational `
      tests\test_auth_session_api.py `
      --basetemp=.pytest_tmp

Result:

    88 passed

## Git Evidence

Implementation commit:

    8088aaf feat: add backend auth session endpoint

Later dependent frontend session commit:

    483bd4d feat: add frontend auth session context

Mini-EPIC 31.7 closure commit:

    0cd3e06 docs: close mini epic 31.7 frontend auth session context

## Closure Assessment

Mini-EPIC 31.6 is closed.

The backend now exposes a current authenticated session endpoint that returns backend-derived principal and permission data.

This established the correct contract for Mini-EPIC 31.7, where the frontend consumed the backend session endpoint without inventing roles or permissions locally.

The authentication and authorization boundary remains backend-owned.