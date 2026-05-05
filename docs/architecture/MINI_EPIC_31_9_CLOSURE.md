# Mini-EPIC 31.9 Closure - Permission-Aware Action Controls & Product Surface Truthfulness

## Status

Closed.

## Context

Mini-EPIC 31.8 made the frontend Admin Ops navigation permission-aware by using the backend-derived current session context.

Mini-EPIC 31.9 extends the same principle to product-facing action controls.

The goal was not to create frontend RBAC. The goal was to make the product surface truthful: sensitive UI actions should not appear available when the backend-derived session does not contain the required permission.

Backend authorization remains the real enforcement layer.

## Confirmed Starting State

- Mini-EPIC 31.8 was closed.
- Commit already pushed:
  - 6e45267 feat: make admin navigation permission-aware
- Branch main was up to date with origin/main.
- Working tree was clean.
- Frontend lint passed before this mini-epic.
- Frontend build passed before this mini-epic.
- Backend was not touched in Mini-EPIC 31.8.
- Frontend already had:
  - AuthSessionProvider
  - useAuthSession
  - backend-derived permissions
  - hasPermission(permission)
  - authenticated/loading/unauthenticated/error session states
- Admin Ops navigation already used backend-derived operations.view_metrics.

## Inspection Performed

Repository inspection was performed before implementation, as required.

Inspected frontend surfaces:

- ui/invomatch-ui/src/pages/RunDetailPage.tsx
- ui/invomatch-ui/src/components/ReviewPanel.tsx
- ui/invomatch-ui/src/components/ActionPanel.tsx
- ui/invomatch-ui/src/components/ExportPanel.tsx
- ui/invomatch-ui/src/services/api.ts
- ui/invomatch-ui/src/auth/AuthSessionProvider.tsx
- ui/invomatch-ui/src/auth/sessionTypes.ts
- ui/invomatch-ui/src/auth/useAuthSession.ts

Inspected backend authorization and permission sources:

- src/invomatch/domain/security/permission.py
- src/invomatch/services/security/permission_matrix.py
- src/invomatch/api/actions.py
- src/invomatch/api/export.py
- src/invomatch/api/export_artifacts.py
- src/invomatch/api/review_cases.py
- src/invomatch/api/reconciliation_runs.py
- src/invomatch/api/security/dependencies.py

## Backend Permission Evidence

Existing backend permission names were reused. No frontend-only permission names were invented.

Relevant backend permissions identified:

- runs.read_review
- actions.resolve_review
- actions.export_run
- exports.download_direct
- artifacts.list
- artifacts.read_metadata
- artifacts.download
- operations.view_metrics

Relevant backend action mapping:

- resolve_review maps to Permission.ACTIONS_RESOLVE_REVIEW.
- export_run maps to Permission.ACTIONS_EXPORT_RUN.

Relevant backend artifact/download mapping:

- artifact list requires Permission.ARTIFACTS_LIST.
- artifact metadata requires Permission.ARTIFACTS_READ_METADATA.
- artifact download requires Permission.ARTIFACTS_DOWNLOAD.
- direct run export requires Permission.EXPORTS_DOWNLOAD_DIRECT.

## Implementation Summary

### ActionPanel

Updated:

- ui/invomatch-ui/src/components/ActionPanel.tsx

Implemented:

- Imported useAuthSession.
- Added constant ACTIONS_EXPORT_RUN_PERMISSION = actions.export_run.
- Export Run button is enabled only when:
  - session status is authenticated; and
  - hasPermission("actions.export_run") is true; and
  - no action request is currently loading.
- The click handler returns early if the permission is not present.
- Loading, unauthenticated, and error session states do not grant action access.
- Missing permission produces an honest operator-facing message.
- No role name is checked in the frontend.
- No frontend RBAC matrix was introduced.

### ExportPanel

Updated:

- ui/invomatch-ui/src/components/ExportPanel.tsx

Implemented:

- Imported useAuthSession.
- Added constant ARTIFACTS_DOWNLOAD_PERMISSION = artifacts.download.
- Artifact download links are rendered only when:
  - the artifact has a download_url; and
  - session status is authenticated; and
  - hasPermission("artifacts.download") is true.
- Loading, unauthenticated, error, and missing-permission states do not show download links.
- When download URLs exist but the current session cannot download, the UI shows an honest explanatory message.
- Existing artifact metadata display remains usable.

## Deliberate Non-Changes

Backend was not changed.

No endpoint contract was changed.

No login/logout was added.

No OAuth/OIDC was added.

No frontend role calculation was added.

No frontend permission matrix was added.

No permission names were invented.

ReviewPanel was not changed because the current component only displays review_summary already returned by RunView; it does not currently expose a sensitive review action.

RunDetailPage was not changed because the truthful behavior is now encapsulated in the action/download surface components themselves.

Direct run export via getRunExport() was not exposed in the current UI, so no UI control was added for exports.download_direct.

## Validation

Frontend validation was executed.

Commands executed:

- cd C:\dev\InvoMatch\ui\invomatch-ui
- npm run lint
- npm run build

Result:

- npm run lint passed.
- npm run build passed.
- Vite production build completed successfully.
- Build output included:
  - dist/index.html
  - dist/assets/index-DGNrK5qb.css
  - dist/assets/index-BdhK-dto.js

Backend validation was not required because backend source and endpoint contracts were not changed.

## Exit Criteria Check

- Sensitive frontend action controls use backend-derived permissions only: satisfied.
- No fake frontend RBAC introduced: satisfied.
- Loading, unauthenticated, and error states do not grant UI access: satisfied.
- Existing product read/navigation flows remain usable: satisfied.
- Backend authorization remains unchanged and authoritative: satisfied.
- Backend endpoint contracts remain unchanged: satisfied.
- Frontend lint passes: satisfied.
- Frontend build passes: satisfied.
- Backend/system validation pack remains green if backend is touched: not applicable; backend was not touched.
- Closure doc added: satisfied by this document.
- Commit and push: pending at time of writing.
- Working tree clean: pending after commit and push.

## Files Changed

- ui/invomatch-ui/src/components/ActionPanel.tsx
- ui/invomatch-ui/src/components/ExportPanel.tsx
- docs/architecture/MINI_EPIC_31_9_CLOSURE.md

## Final Assessment

Mini-EPIC 31.9 closes a real product truthfulness gap.

Before this change, the frontend displayed the Export Run action without checking whether the current backend-derived session contained the corresponding backend permission.

After this change, product-facing action and artifact download controls are permission-aware without pretending that frontend logic is a security boundary.

The backend remains authoritative. The frontend now presents a more honest operator surface.