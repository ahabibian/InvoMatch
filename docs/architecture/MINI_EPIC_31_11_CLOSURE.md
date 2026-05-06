# Mini-EPIC 31.11 Closure - Permission-Aware Input Submission Surface & Upload Failure Truthfulness

## Status

Closed.

## Context

Mini-EPIC 31.10 made product read surfaces permission-aware by relying on the backend-derived auth session and avoiding frontend role calculation.

Mini-EPIC 31.11 extends that same product truthfulness rule to the input submission surface.

The objective was not to add authentication, login/logout, OAuth/OIDC, or frontend RBAC. The objective was to stop the upload/input surface from implying that JSON or file submission is available when the current backend-derived session does not include the required backend permission.

## Confirmed Starting State

- Previous commit:
  - b33a703 feat: make product read surfaces permission-aware
- Branch:
  - main
- Branch state:
  - up to date with origin/main
- Working tree:
  - clean
- Frontend lint:
  - previously passing
- Frontend build:
  - previously passing
- Backend:
  - not touched in Mini-EPIC 31.10

## Repository Inspection

Inspection was performed before implementation.

Frontend files inspected:

- ui/invomatch-ui/src/pages/UploadPage.tsx
- ui/invomatch-ui/src/App.tsx
- ui/invomatch-ui/src/services/api.ts
- ui/invomatch-ui/src/auth/AuthSessionProvider.tsx
- ui/invomatch-ui/src/auth/sessionTypes.ts
- existing permission-aware surfaces:
  - RunListPage
  - RunDetailPage
  - ReviewPanel
  - ExportPanel
  - ActionPanel

Backend files inspected:

- src/invomatch/domain/security/permission.py
- src/invomatch/services/security/permission_matrix.py
- src/invomatch/api/routes/input_boundary.py
- src/invomatch/api/reconciliation_runs.py
- src/invomatch/api/auth_session.py
- tests/test_auth_session_api.py

## Backend Permission Evidence

The backend defines the input submission permission as:

- Permission.INPUT_SUBMIT = input.submit

The backend input boundary requires Permission.INPUT_SUBMIT for both product input submission endpoints:

- POST /api/reconciliation/input/json
- POST /api/reconciliation/input/file

The backend also defines related permissions:

- Permission.INPUT_VIEW = input.view
- Permission.RUNS_CREATE = runs.create
- Permission.RUNS_CREATE_FROM_INGESTION = runs.create_from_ingestion

No new permission names were invented.

The frontend now uses only the inspected backend-derived permission value:

- input.submit

## Implementation Summary

Updated:

- ui/invomatch-ui/src/pages/UploadPage.tsx

Changes made:

1. Added backend-derived session awareness through useAuthSession.
2. Added a local constant for the inspected backend permission:
   - INPUT_SUBMIT_PERMISSION = input.submit
3. JSON submission is only available when:
   - session status is authenticated
   - session permissions include input.submit
4. File upload is only available when:
   - session status is authenticated
   - session permissions include input.submit
5. Loading, unauthenticated, session-error, and missing-permission states now disable the input controls.
6. Missing permission is shown truthfully as a permission issue, not as malformed input or processing failure.
7. JSON submit now reports:
   - invalid local JSON as invalid JSON
   - HTTP 401 as unauthenticated submission failure
   - HTTP 403 as backend authorization denial for input.submit
8. File upload now calls the existing frontend API client function:
   - submitFileInput(file)
9. File upload 401/403 failures are now shown as authentication/authorization failures, not generic upload or processing failures.
10. Backend endpoint contracts were not changed.
11. No login/logout was added.
12. No OAuth/OIDC was added.
13. No frontend role-name checks were added.
14. No frontend RBAC matrix was introduced.

## Product Truthfulness Correction

Before this Mini-EPIC, the File Upload button did not submit the selected file to the backend.

It only displayed:

- File selected: filename

That was not a truthful product surface.

The file upload control now calls:

- submitFileInput(file)

and displays the backend response, matching the JSON submission behavior.

## Backend Changes

None.

Backend authorization remains authoritative.

## Frontend Authorization Boundary

The frontend only uses backend-derived session permissions to decide whether controls should appear usable.

The frontend does not enforce security.

The frontend only prevents misleading operator affordances.

The backend remains the enforcement layer.

## Validation Commands

All commands were executed in PowerShell.

Frontend lint command:

- cd C:\dev\InvoMatch\ui\invomatch-ui
- npm run lint

Frontend lint result:

- Passed.

Frontend build command:

- cd C:\dev\InvoMatch\ui\invomatch-ui
- npm run build

Frontend build result:

- Passed.

## Backend Validation

Backend validation was not required because backend code and endpoint contracts were not changed.

## Exit Criteria Result

- Upload/input surface does not imply submission access when backend-derived permissions are missing.
- JSON submission controls are disabled truthfully when access is unavailable.
- File upload controls are disabled truthfully when access is unavailable.
- Loading, unauthenticated, session-error, and missing-permission states do not grant UI access.
- 401 input submission failures are displayed as authentication failures.
- 403 input submission failures are displayed as backend authorization denials for input.submit.
- No fake frontend RBAC was introduced.
- No role-name checks were added.
- No permission names were invented.
- Existing authorized JSON input flow remains usable.
- Existing authorized file input flow is now actually wired to the backend.
- Backend authorization remains unchanged and authoritative.
- Backend endpoint contracts remain unchanged.
- Frontend lint passed.
- Frontend build passed.
- Closure doc added.

## Files Changed

- ui/invomatch-ui/src/pages/UploadPage.tsx
- docs/architecture/MINI_EPIC_31_11_CLOSURE.md

## Final State

Expected final repository state after commit and push:

- Commit created:
  - feat: make input submission surface permission-aware
- Branch:
  - main
- Remote:
  - pushed to origin/main
- Working tree:
  - clean