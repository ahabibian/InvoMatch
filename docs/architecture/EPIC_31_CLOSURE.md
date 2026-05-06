# EPIC 31 Closure - Frontend Operational Visibility & Backend-Derived Permission-Aware Product Surface

## Status

Closed.

## Closure Date

2026-05-06

## Purpose

EPIC 31 closes the frontend operational visibility and backend-derived permission-aware product surface work.

This EPIC moved the frontend from a mostly static operator surface toward a more truthful product UI that reflects the current authenticated session returned by the backend.

The important boundary is strict:

- the backend remains authoritative for authentication and authorization;
- the frontend does not enforce authorization;
- the frontend does not calculate roles;
- the frontend does not invent permission names;
- the frontend does not maintain a frontend RBAC matrix;
- the frontend does not perform role-name checks;
- the frontend only consumes backend-derived session permissions to avoid showing misleading UI affordances.

The work is not a login system, not an OAuth/OIDC integration, and not a frontend authorization layer.

## Consolidated Mini-EPICs

EPIC 31 consolidates the following completed work.

| Mini-EPIC | Title | Closure / Evidence |
|---|---|---|
| 31.0 | Operational Visibility Layer | docs/architecture/OPERATIONAL_VISIBILITY_CLOSURE.md |
| 31.1 | Operational Visibility Contract Hardening | docs/architecture/MINI_EPIC_31_1_CLOSURE.md |
| 31.2 | Operational Visibility UI Integration Readiness | docs/architecture/MINI_EPIC_31_2_CLOSURE.md |
| 31.3 | Admin-Only Operational Visibility Dashboard | docs/architecture/MINI_EPIC_31_3_CLOSURE.md |
| 31.4 | Role-Aware Admin Navigation & Operational Dashboard Hardening | docs/architecture/MINI_EPIC_31_4_CLOSURE.md |
| 31.5 | Frontend Auth Session Context Foundation | docs/architecture/MINI_EPIC_31_5_CLOSURE.md and docs/architecture/MINI_EPIC_31_5_FRONTEND_AUTH_SESSION_CONTEXT.md |
| 31.6 | Backend Current Session Endpoint Contract | docs/architecture/MINI_EPIC_31_6_CLOSURE.md |
| 31.7 | Frontend API Token Injection & Backend-Derived Session Context | docs/architecture/MINI_EPIC_31_7_CLOSURE.md |
| 31.8 | Role-Aware Navigation Using Backend-Derived Permissions | docs/architecture/MINI_EPIC_31_8_CLOSURE.md |
| 31.9 | Permission-Aware Action Controls & Product Surface Truthfulness | docs/architecture/MINI_EPIC_31_9_CLOSURE.md |
| 31.10 | Permission-Aware Product Read Surfaces & API Failure Truthfulness | docs/architecture/MINI_EPIC_31_10_CLOSURE.md |
| 31.11 | Permission-Aware Input Submission Surface & Upload Failure Truthfulness | docs/architecture/MINI_EPIC_31_11_CLOSURE.md |

## Final Architecture Outcome

EPIC 31 creates a clearer separation between backend authorization enforcement and frontend product truthfulness.

The backend owns:

- authentication;
- token resolution;
- principal resolution;
- role-to-permission mapping;
- endpoint and service authorization;
- permission names and semantics;
- 401 / 403 behavior;
- tenant-aware authorization context.

The frontend owns:

- consuming the backend session endpoint;
- storing the current backend-derived session state;
- exposing session loading / authenticated / unauthenticated / error states;
- checking whether a backend-derived permission string exists in the current session response;
- hiding or disabling UI affordances that the current session should not be led to believe are available;
- showing truthful permission and backend-denial messages.

This means the frontend is product-truthful, not security-authoritative.

The backend remains the enforcement boundary.

## Backend Session Contract

EPIC 31 added the backend current-session product contract:

- GET /api/auth/session
- implementation: src/invomatch/api/auth_session.py
- response model: src/invomatch/api/product_models/auth_session.py

The endpoint resolves the authenticated principal through the existing backend authentication dependency and returns:

- user_id
- username
- role
- status
- tenant_id
- auth_source
- ordered backend-derived permissions

The returned permissions are derived from the backend permission matrix:

- src/invomatch/services/security/permission_matrix.py
- ROLE_PERMISSIONS
- get_permissions_for_role(role)

The frontend does not derive these permissions locally.

## Frontend Session Context

EPIC 31 added the frontend session context and API transport foundation:

- ui/invomatch-ui/src/services/api.ts
- ui/invomatch-ui/src/auth/AuthSessionContext.ts
- ui/invomatch-ui/src/auth/AuthSessionProvider.tsx
- ui/invomatch-ui/src/auth/sessionTypes.ts
- ui/invomatch-ui/src/auth/useAuthSession.ts
- ui/invomatch-ui/src/main.tsx

The frontend API client injects Authorization: Bearer <token> from VITE_API_AUTH_TOKEN when configured.

The frontend session context exposes:

- session
- status
- error
- user
- permissions
- hasPermission(permission)
- reloadSession()

This is intentionally minimal. It is not a login workflow.

## Permission-Aware Surfaces

### Operational Visibility Navigation

File:

- ui/invomatch-ui/src/App.tsx

The Admin Ops navigation entry is only rendered when the backend-derived session includes:

- operations.view_metrics

The operational dashboard still depends on backend authorization. Hiding the navigation does not replace backend enforcement.

### Operational Visibility Dashboard

File:

- ui/invomatch-ui/src/pages/OperationalVisibilityPage.tsx

The dashboard now communicates that backend authorization remains the source of truth and handles authorization-related API failures truthfully.

Operational visibility endpoint contracts were hardened earlier in this EPIC and documented through:

- docs/architecture/OPERATIONAL_VISIBILITY_API_CONTRACT.md

### Product Action Controls

File:

- ui/invomatch-ui/src/components/ActionPanel.tsx

The export action control checks backend-derived session permission:

- actions.export_run

The frontend does not grant export capability. It only avoids presenting the export action as available when the backend-derived session does not include the permission.

### Product Read Surfaces

Files:

- ui/invomatch-ui/src/pages/RunListPage.tsx
- ui/invomatch-ui/src/pages/RunDetailPage.tsx
- ui/invomatch-ui/src/components/ReviewPanel.tsx
- ui/invomatch-ui/src/components/ExportPanel.tsx

Permission-aware read surfaces include:

| Surface | Permission(s) used |
|---|---|
| Run list | runs.list |
| Run detail | runs.read_view |
| Review summary | runs.read_review |
| Artifact metadata | artifacts.list, artifacts.read_metadata |
| Artifact download | artifacts.download |

The frontend avoids misleading the user when these permissions are missing and reports backend 403 failures as authorization denial instead of generic product failure.

### Input Submission Surface

File:

- ui/invomatch-ui/src/pages/UploadPage.tsx

The JSON and file input submission controls check backend-derived session permission:

- input.submit

When missing, the UI disables the relevant controls and displays truthful copy instead of implying that submission is available.

Backend authorization remains authoritative for the actual submission endpoints.

## Explicit Non-Goals

EPIC 31 did not implement:

- login;
- logout;
- signup;
- password handling;
- OAuth;
- OIDC;
- refresh-token lifecycle;
- browser token storage strategy;
- frontend RBAC matrix;
- frontend role-to-permission mapping;
- frontend role-name checks;
- frontend authorization enforcement;
- frontend-invented permission names;
- backend security weakening;
- new backend permissions solely for UI convenience;
- replacing backend authorization with UI hiding.

These are deliberate non-goals.

EPIC 31 improves product truthfulness. It does not turn the frontend into the authorization authority.

## Authorization Boundary Confirmation

EPIC 31 preserves the existing backend authorization boundary.

The frontend:

- reads permissions from /api/auth/session;
- checks whether the current session includes specific backend-defined permission strings;
- hides or disables misleading UI affordances;
- shows truthful unavailable / denied messages;
- does not decide whether a backend operation is allowed.

The backend:

- resolves the authenticated principal;
- derives permissions from backend role configuration;
- enforces protected endpoint access;
- returns 401 / 403 behavior;
- remains the only trusted authorization layer.

Any frontend permission check is an affordance-truthfulness check only.

## Commit History Referenced

Relevant commit history observed during closure:

- 4c615d6 feat: make input submission surface permission-aware
- b33a703 feat: make product read surfaces permission-aware
- 92e9342 feat: make product actions permission-aware
- 6e45267 feat: make admin navigation permission-aware
- 708bfc1 docs: close mini epic 31.5 frontend auth session foundation
- b3fa26e docs: close mini epic 31.6 backend auth session endpoint
- 0cd3e06 docs: close mini epic 31.7 frontend auth session context
- 483bd4d feat: add frontend auth session context
- 8088aaf feat: add backend auth session endpoint
- 05be50e docs: document frontend auth session context foundation
- 8c48528 feat: harden admin operational dashboard boundary
- 42f833d feat: add admin operational visibility dashboard
- 944fe37 feat: prepare operational visibility UI client
- 653d435 docs: close mini epic 31.1 operational visibility contracts
- b8a94bd feat: harden operational visibility response contracts
- 9580798 docs: close operational visibility layer
- 28e28be docs: document operational visibility endpoint protection
- f88f7f4 feat: add operational alert visibility policy
- 7284c09 feat: add operational metrics visibility API

## Validation Evidence

Fresh validation was executed before creating this closure.

### Initial Repository State

On branch main. Branch was up to date with origin/main. Working tree was clean.

### Backend Auth Session Tests

Command:

$env:PYTHONPATH = "src"
pytest -q tests\test_auth_session_api.py --basetemp=.pytest_tmp

Result:

6 passed in 6.07s

### Backend Permission / Security / Product Surface Tests

Command:

pytest -q tests\system\test_permission_boundary_enforcement.py tests\system\test_security_boundary_enforcement.py tests\test_actions_api.py tests\test_export_api.py tests\test_export_artifact_api.py tests\test_review_api.py tests\test_reconciliation_runs_api.py tests\test_input_boundary_api.py --basetemp=.pytest_tmp

Result:

52 passed in 20.22s

### Operational Visibility Tests

Command:

pytest -q tests\operational --basetemp=.pytest_tmp

Result:

78 passed in 29.07s

### Frontend Lint

Command:

cd C:\dev\InvoMatch\ui\invomatch-ui
npm run lint

Result:

eslint completed with no reported errors.

### Frontend Build

Command:

npm run build

Result:

tsc -b and vite build completed successfully. Vite transformed 28 modules and built successfully in 537ms.

### Final Repository State Before Closure Document Creation

On branch main. Branch was up to date with origin/main. Working tree was clean.

## Exit Criteria Review

| Exit Criteria | Status |
|---|---|
| All completed Mini-EPICs 31.0 through 31.11 are listed | Satisfied |
| Final architecture outcome is documented | Satisfied |
| Explicit non-goals are documented | Satisfied |
| Permission-aware surfaces are summarized | Satisfied |
| Validation evidence is recorded | Satisfied |
| Commit history is referenced | Satisfied |
| Closure doc is added | Satisfied by this document |
| Commit and push complete | To be completed after committing this document |
| Working tree clean | To be verified after commit and push |

## Final Closure Statement

EPIC 31 is closed.

The frontend now has operational visibility and permission-aware product surfaces that are truthful to the current backend-derived session state.

The work deliberately avoids fake frontend RBAC. It does not implement login/logout, OAuth/OIDC, a frontend RBAC matrix, role-name checks, or local permission calculation.

The backend remains authoritative for authentication and authorization. The frontend uses backend-derived permissions only to avoid misleading UI affordances.