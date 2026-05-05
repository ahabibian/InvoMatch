# Mini-EPIC 31.10 Closure - Permission-Aware Product Read Surfaces & API Failure Truthfulness

## Status

Closed.

## Context

Mini-EPIC 31.9 made product-facing sensitive action controls permission-aware using backend-derived session permissions.

Mini-EPIC 31.10 extends that truthfulness to product-facing read surfaces and frontend API failure handling without moving authorization enforcement into the frontend.

The backend remains authoritative. The frontend only uses backend-derived session permissions to avoid implying access that the current authenticated session does not have.

## Confirmed Starting State

- Previous committed state:
  - 92e9342 feat: make product actions permission-aware
- Branch:
  - main
- Remote state:
  - up to date with origin/main
- Working tree before implementation:
  - clean
- Backend:
  - not touched

## Inspection Performed

The implementation started with repository inspection only.

Inspected frontend surfaces:

- ui/invomatch-ui/src/pages/RunListPage.tsx
- ui/invomatch-ui/src/pages/RunDetailPage.tsx
- ui/invomatch-ui/src/components/ReviewPanel.tsx
- ui/invomatch-ui/src/components/ExportPanel.tsx
- ui/invomatch-ui/src/pages/OperationalVisibilityPage.tsx
- ui/invomatch-ui/src/components/ActionPanel.tsx
- ui/invomatch-ui/src/services/api.ts
- ui/invomatch-ui/src/auth/AuthSessionProvider.tsx
- ui/invomatch-ui/src/auth/sessionTypes.ts
- ui/invomatch-ui/src/auth/useAuthSession.ts

Inspected backend permission sources and authorization checks:

- src/invomatch/domain/security/permission.py
- src/invomatch/services/security/permission_matrix.py
- src/invomatch/api/reconciliation_runs.py
- src/invomatch/api/review_cases.py
- src/invomatch/api/export_artifacts.py
- src/invomatch/api/actions.py
- src/invomatch/api/operations.py
- src/invomatch/api/security/dependencies.py
- tests/test_auth_session_api.py

Confirmed permission names were taken from backend-defined permission constants and existing auth session output.

No frontend-only permission names were invented.

## Backend Permission Evidence

Backend-defined permissions used by this mini-epic:

- runs.list
- runs.read_view
- runs.read_review
- artifacts.list
- artifacts.read_metadata
- artifacts.download

Observed backend authorization checks:

- GET /api/reconciliation/runs
  - guarded by Permission.RUNS_LIST
- GET /api/reconciliation/runs/{run_id}/view
  - guarded by Permission.RUNS_READ_VIEW
- GET /api/reconciliation/runs/{run_id}/review
  - guarded by Permission.RUNS_READ_REVIEW
- GET /api/reconciliation/runs/{run_id}/exports
  - guarded by Permission.ARTIFACTS_LIST
- GET /api/reconciliation/exports/{artifact_id}
  - guarded by Permission.ARTIFACTS_READ_METADATA
- GET /api/reconciliation/exports/{artifact_id}/download
  - guarded by Permission.ARTIFACTS_DOWNLOAD

## Changes Made

### Run list read surface

Updated:

- ui/invomatch-ui/src/pages/RunListPage.tsx

Behavior:

- Loads the run list only when the backend-derived session is authenticated and includes runs.list.
- Shows a truthful unavailable state while session access is loading, unauthenticated, failed, or missing runs.list.
- Maps backend 401 to an authentication denial message.
- Maps backend 403 to a backend authorization denial message for runs.list.
- Clears stale run list data when access is unavailable or backend access is denied.

### Run detail read surface

Updated:

- ui/invomatch-ui/src/pages/RunDetailPage.tsx

Behavior:

- Loads run view only when the backend-derived session is authenticated and includes runs.read_view.
- Shows a truthful unavailable state while session access is loading, unauthenticated, failed, or missing runs.read_view.
- Maps backend 401 to an authentication denial message.
- Maps backend 403 to a backend authorization denial message for runs.read_view.
- Clears stale run detail data when access is unavailable or backend access is denied.

### Review summary surface

Updated:

- ui/invomatch-ui/src/components/ReviewPanel.tsx

Behavior:

- Shows review summary only when the backend-derived session is authenticated and includes runs.read_review.
- Shows a truthful hidden/unavailable message when session state or permissions do not allow review visibility.
- Does not introduce review role checks.
- Does not call a backend review endpoint itself.

### Export artifact surface

Updated:

- ui/invomatch-ui/src/components/ExportPanel.tsx

Behavior:

- Shows artifact metadata/list content only when the backend-derived session is authenticated and includes both:
  - artifacts.list
  - artifacts.read_metadata
- Shows artifact download links only when the backend-derived session is authenticated and includes:
  - artifacts.download
- Shows truthful messages when metadata or download affordances are unavailable.
- Does not weaken backend artifact endpoint authorization.
- Does not introduce frontend role checks.

## Explicit Non-Changes

This mini-epic did not:

- add login/logout;
- add OAuth/OIDC;
- add frontend role calculation;
- add role-name checks;
- invent permission names;
- change backend permission constants;
- change backend route contracts;
- change backend authorization behavior;
- add a frontend RBAC matrix.

## Validation

Frontend lint command:

    cd C:\dev\InvoMatch\ui\invomatch-ui
    npm run lint

Result:

    > invomatch-ui@0.0.0 lint
    > eslint .

The command completed successfully.

Frontend build command:

    cd C:\dev\InvoMatch\ui\invomatch-ui
    npm run build

Result:

    > invomatch-ui@0.0.0 build
    > tsc -b && vite build

    vite v8.0.8 building client environment for production...
    28 modules transformed.
    built successfully.

The command completed successfully.

The build was run twice successfully during validation.

## Backend Validation

Backend code was not touched.

Because this mini-epic only changed frontend read-surface rendering and frontend permission-aware UI behavior, backend/system validation was not required for this closure.

Backend authorization remains the enforcement layer.

## Exit Criteria Review

- Product read surfaces do not imply access when backend-derived permissions are missing.
  - Met.
- 401 and 403 API failures are displayed truthfully in the frontend.
  - Met for run list and run detail read surfaces.
- No fake frontend RBAC is introduced.
  - Met.
- No role-name checks are added.
  - Met.
- No permission names are invented.
  - Met.
- Existing authorized product flows remain usable.
  - Met.
- Backend authorization remains unchanged and authoritative.
  - Met.
- Backend endpoint contracts remain unchanged.
  - Met.
- Frontend lint passes.
  - Met.
- Frontend build passes.
  - Met.
- Backend/system validation pack remains green if backend is touched.
  - Not applicable; backend was not touched.
- Closure doc is added.
  - Met by this document.
- Commit and push complete.
  - Pending at time of document creation.
- Working tree clean.
  - Pending after commit and push.

## Closure Decision

Mini-EPIC 31.10 is implementation-complete once this closure document is committed and pushed with the frontend changes.

The resulting product UI is more truthful: it no longer presents run list, run detail, review summary, artifact metadata, or artifact download affordances as available when the current backend-derived session does not include the corresponding permissions.

Authorization remains backend-owned.