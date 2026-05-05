# Mini-EPIC 31.5 - Frontend Auth Session Context & Role Claims Foundation

## Status

Implemented as documentation-only foundation.

No frontend session context was added because the repository does not currently expose a backend current-user/session endpoint that the frontend can truthfully consume.

## Confirmed Previous State

Mini-EPIC 31.4 was closed with commit:

- `8c48528 feat: harden admin operational dashboard boundary`

Confirmed state before Mini-EPIC 31.5:

- Branch `main` was pushed to `origin/main`.
- Working tree was clean before this Mini-EPIC.
- Frontend lint had passed:
  - `npm run lint`
- Frontend build had passed:
  - `npm run build`
- Backend/system regression pack had passed:
  - `82 passed in 19.21s`
- Admin operational dashboard exists:
  - `ui/invomatch-ui/src/pages/OperationalVisibilityPage.tsx`
- App navigation includes:
  - `Admin Ops`
- Mini-EPIC 31.4 confirmed frontend limitation:
  - no frontend user context
  - no frontend session context
  - no frontend role context
  - no frontend permission context
  - no frontend token/header injection model
- Backend authorization remains source of truth:
  - `operations.view_metrics`

## Goal

Introduce a minimal, explicit frontend auth/session context foundation so future navigation and admin UI behavior can become role-aware without fake authorization logic.

The outcome of repository inspection shows that the correct foundation for this Mini-EPIC is not a React context implementation yet. The correct foundation is to document the current backend/frontend auth reality and define the backend contract required before truthful frontend role-aware behavior can be implemented.

## Repository Evidence

### Backend Auth Reality

The backend already has an explicit authenticated principal model:

- File:
  - `src/invomatch/domain/security/principal.py`

Current principal fields:

- `user_id`
- `username`
- `role`
- `status`
- `auth_source`
- `tenant_id`

The backend has explicit role values:

- File:
  - `src/invomatch/domain/security/role.py`

Current roles:

- `viewer`
- `operator`
- `admin`

The backend has explicit permission values:

- File:
  - `src/invomatch/domain/security/permission.py`

Relevant operational permissions include:

- `operations.view_metrics`
- `operations.execute_recovery`
- `operations.execute_startup_repair`
- `operations.manage_admin_surface`

The backend has a permission matrix:

- File:
  - `src/invomatch/services/security/permission_matrix.py`

Confirmed behavior:

- `viewer` does not have `operations.view_metrics`
- `operator` does not have `operations.view_metrics`
- `admin` has `operations.view_metrics`

The backend has token-based authentication:

- File:
  - `src/invomatch/services/security/authentication_service.py`
- File:
  - `src/invomatch/services/security/token_provider.py`

Current authentication behavior:

- Reads `Authorization: Bearer <token>`
- Rejects missing authorization header
- Rejects malformed authorization header
- Rejects empty bearer token
- Rejects unknown token
- Rejects revoked token
- Rejects expired token
- Returns an `AuthenticatedPrincipal` when valid

The backend has permission-based authorization:

- File:
  - `src/invomatch/services/security/authorization_service.py`
- File:
  - `src/invomatch/api/security/dependencies.py`

Current authorization behavior:

- Requires active user
- Checks role permission via `role_has_permission`
- Returns 403 for missing permission
- Records security audit events

### Backend Operational Authorization

Operational visibility endpoints require backend permission enforcement:

- File:
  - `src/invomatch/api/operations.py`

Required permission:

- `Permission.OPERATIONS_VIEW_METRICS`
- value:
  - `operations.view_metrics`

This remains the enforcement source of truth.

### Backend Route Registration Reality

Registered routers are defined in:

- File:
  - `src/invomatch/main.py`

Currently registered routers:

- `input_boundary_router`
- `health_router`
- `audit_events_router`
- `operations_router`
- `reconciliation_runs_router`
- `review_cases_router`
- `actions_router`
- `export_router`
- `export_artifacts_router`

There is currently no registered auth/session/current-user router.

No route was found for:

- `/api/auth/session`
- `/api/session`
- `/api/me`
- `/api/current-user`

### Frontend Auth Reality

The frontend app shell is defined in:

- File:
  - `ui/invomatch-ui/src/App.tsx`

Current state:

- Local `viewMode` state only
- No current user state
- No session state
- No role state
- No permission state
- `Admin Ops` remains visible
- Existing comment explicitly warns not to add fake frontend RBAC

The frontend API client is defined in:

- File:
  - `ui/invomatch-ui/src/services/api.ts`

Current request behavior:

- Uses `fetch`
- Uses `VITE_API_BASE_URL`
- Does not inject `Authorization`
- Does not read a token
- Does not manage session state
- Does not expose `getCurrentUser`
- Does not expose `getSession`
- Does not expose `hasPermission`
- Does not expose `hasRole`

Operational visibility frontend behavior is defined in:

- File:
  - `ui/invomatch-ui/src/pages/OperationalVisibilityPage.tsx`

Current behavior:

- Calls operational endpoints directly.
- Handles 401/403 as backend authorization failures.
- States clearly that frontend role-aware navigation is not available.
- Keeps backend authorization as the security boundary.

## Decision

No frontend auth/session context is added in this Mini-EPIC.

Reason:

A frontend `CurrentUser`, `Session`, `hasRole`, or `hasPermission` helper would require real backend-backed session data. The current backend has authentication and authorization primitives, but it does not expose a current-user/session endpoint for the frontend to consume.

Adding any of the following now would be misleading:

- hardcoded `admin`
- local fake `CurrentUser`
- frontend-only role inference
- frontend-only permission inference
- local `hasPermission("operations.view_metrics")` without backend session data

This would create a false security model and make the UI appear role-aware when it is not.

## Explicit Non-Implementation

The following were intentionally not implemented:

- React auth/session context
- frontend `CurrentUser` type wired to fake data
- frontend `Session` type wired to fake data
- `hasRole("admin")`
- `hasPermission("operations.view_metrics")`
- Admin Ops navigation hiding based on fake state
- token storage
- token injection
- login/logout
- OAuth/OIDC
- Redux/Zustand/MobX

## Future Backend Contract Proposal

Before frontend role-aware navigation can be implemented truthfully, the backend should expose a current session endpoint.

### Proposed Endpoint

HTTP method:

- `GET`

Path:

- `/api/auth/session`

Required request header:

- `Authorization: Bearer <token>`

### Authorization Semantics

The endpoint should:

- require a valid authenticated principal
- reject missing/invalid/expired/revoked tokens with existing 401 behavior
- reject inactive users with existing 403 behavior
- return the current authenticated principal
- return backend-derived permissions for the current role
- not allow the frontend to submit or override role/permission claims

### Proposed Response Shape

Example response:

{
  "user": {
    "user_id": "admin-1",
    "username": "admin",
    "role": "admin",
    "status": "active",
    "tenant_id": "tenant-demo",
    "auth_source": "internal_token"
  },
  "permissions": [
    "input.submit",
    "input.view",
    "runs.create",
    "runs.create_from_ingestion",
    "runs.list",
    "runs.read",
    "runs.read_view",
    "runs.read_review",
    "actions.resolve_review",
    "actions.export_run",
    "exports.download_direct",
    "artifacts.list",
    "artifacts.read_metadata",
    "artifacts.download",
    "operations.view_metrics",
    "operations.execute_recovery",
    "operations.execute_startup_repair",
    "operations.manage_admin_surface"
  ]
}

### Proposed Frontend Follow-up

Once the backend endpoint exists, a later Mini-EPIC can add:

- `CurrentUser` frontend type
- `Session` frontend type
- `getCurrentSession()` API client function
- lightweight React context
- session loading/error state
- truthful helpers:
  - `hasRole("admin")`
  - `hasPermission("operations.view_metrics")`
- Admin Ops navigation visibility based on real permission data

The backend must remain the enforcement source of truth. Frontend role-aware navigation is only a user-experience improvement, not a security boundary.

## Product Integrity Rule

The frontend may hide or disable admin navigation only after it has backend-backed session/permission data.

Even after frontend role-aware navigation exists:

- backend authorization remains mandatory
- operational endpoints must continue requiring `operations.view_metrics`
- frontend permissions must never be treated as authoritative enforcement
- operational API response shapes must not drift

## Exit Criteria Evaluation

### Current backend auth/session reality is documented from repository evidence

Satisfied.

Documented files:

- `src/invomatch/domain/security/principal.py`
- `src/invomatch/domain/security/role.py`
- `src/invomatch/domain/security/permission.py`
- `src/invomatch/services/security/authentication_service.py`
- `src/invomatch/services/security/authorization_service.py`
- `src/invomatch/services/security/permission_matrix.py`
- `src/invomatch/services/security/token_provider.py`
- `src/invomatch/api/security/dependencies.py`
- `src/invomatch/main.py`

### Current frontend auth/session reality is documented from repository evidence

Satisfied.

Documented files:

- `ui/invomatch-ui/src/App.tsx`
- `ui/invomatch-ui/src/services/api.ts`
- `ui/invomatch-ui/src/pages/OperationalVisibilityPage.tsx`

### If a real backend session endpoint exists

Not applicable.

Repository inspection found no current-user/session endpoint.

### If no backend session endpoint exists

Satisfied.

- No fake frontend auth was added.
- A contract proposal for a future backend session endpoint is documented.
- Frontend remains honest about the limitation.
- Backend authorization remains the source of truth.

### Existing frontend build passes

Must be re-run after this document is added.

Expected command:

- `cd C:\dev\InvoMatch\ui\invomatch-ui`
- `npm run build`

### Existing frontend lint passes

Must be re-run after this document is added.

Expected command:

- `cd C:\dev\InvoMatch\ui\invomatch-ui`
- `npm run lint`

### Backend/system regression pack remains green

Must be re-run before closure.

Expected command:

- `cd C:\dev\InvoMatch`
- `$env:PYTHONPATH = "src"`
- `pytest -q tests\system\test_happy_path_full_flow.py tests\system\test_review_resolution_flow.py tests\system\test_runtime_failure_terminalization.py tests\system\test_startup_repair_visibility_recovery_alignment.py tests\operational --basetemp=.pytest_tmp`

### No operational API contract drift is introduced

Satisfied by design.

No operational endpoint implementation was changed.
No operational response shape was changed.
No frontend operational model shape was changed.

## Closure Position

Mini-EPIC 31.5 establishes the correct frontend auth/session foundation by refusing to create fake role-aware behavior before the backend exposes a session contract.

The next logical Mini-EPIC should be backend-side:

- add `GET /api/auth/session`
- return backend-derived principal and permissions
- test viewer/operator/admin session responses
- test missing/expired/revoked token behavior
- only then wire frontend session context