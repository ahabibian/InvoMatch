# Mini-EPIC 31.8 Closure - Role-Aware Navigation Using Backend-Derived Permissions

## Status

Closed.

## Context

Mini-EPIC 31.7 added frontend auth session context and permission primitives sourced from the backend session endpoint.

Before this Mini-EPIC, the frontend root was already wrapped in AuthSessionProvider, and useAuthSession() exposed session status, user, permissions, hasPermission(), and reloadSession().

However, the Admin Ops navigation entry was still always visible and explanatory copy still stated that frontend role-aware navigation was not enabled.

## Goal

Use backend-derived frontend session permissions to make navigation and admin entry points truthful without weakening backend authorization.

## Scope Completed

- Inspected current frontend navigation in App.tsx.
- Inspected AuthSessionProvider, useAuthSession, sessionTypes, and AuthSessionContext.
- Inspected OperationalVisibilityPage.
- Inspected api.ts session and operational endpoint contracts.
- Inspected frontend lint/build conventions from package.json.
- Updated App.tsx so Admin Ops is rendered only when:
  - session status is authenticated; and
  - hasPermission("operations.view_metrics") returns true.
- Added a minimal session status display for operator clarity:
  - session status;
  - username and tenant ID when available;
  - auth/session error message when present;
  - refresh session button.
- Ensured loading, unauthenticated, and error states do not produce fake authorization.
- Used backend-derived permissions only.
- Removed stale explanatory copy saying navigation was not role-aware.
- Kept backend authorization as the security boundary.
- Kept operational endpoint contracts unchanged.
- Kept login/logout, OAuth/OIDC, and frontend role calculation out of scope.

## Files Changed

- ui/invomatch-ui/src/App.tsx
- ui/invomatch-ui/src/pages/OperationalVisibilityPage.tsx
- ui/invomatch-ui/src/services/api.ts

## Implementation Notes

App.tsx now defines a single permission constant:

    const OPERATIONS_VIEW_METRICS_PERMISSION = "operations.view_metrics";

The navigation decision is derived from backend session state:

    const canViewOperations =
      authSessionStatus === "authenticated" &&
      hasPermission(OPERATIONS_VIEW_METRICS_PERMISSION);

The Admin Ops button is only rendered when canViewOperations is true.

The rendered view uses effectiveViewMode so an unauthorized, unauthenticated, loading, or error session does not render the operational page:

    const effectiveViewMode =
      viewMode === "operations" && !canViewOperations ? "list" : viewMode;

This avoids synchronous state mutation inside an effect and keeps the view a pure derivation of current UI state and backend-derived permission state.

## Security Boundary

This Mini-EPIC does not make the frontend a security boundary.

The frontend only uses backend-derived session permissions to make navigation truthful.

The backend remains responsible for enforcing operations.view_metrics on operational endpoints.

OperationalVisibilityPage still handles backend 401 and 403 safely and displays an explicit restricted-access message when backend authorization rejects the request.

## Explicit Non-Goals Preserved

- No login/logout added.
- No OAuth/OIDC added.
- No frontend role calculation added.
- No fake frontend RBAC added.
- No backend authorization changes.
- No operational endpoint contract changes.

## Validation Evidence

Frontend lint command:

    cd C:\dev\InvoMatch\ui\invomatch-ui
    npm run lint

Frontend lint result:

    > invomatch-ui@0.0.0 lint
    > eslint .

Frontend build command:

    cd C:\dev\InvoMatch\ui\invomatch-ui
    npm run build

Frontend build result:

    > invomatch-ui@0.0.0 build
    > tsc -b && vite build

    vite v8.0.8 building client environment for production...
    28 modules transformed.
    computing gzip size...
    dist/index.html                   0.46 kB | gzip:  0.30 kB
    dist/assets/index-DGNrK5qb.css    1.78 kB | gzip:  0.81 kB
    dist/assets/index-CoF7_Pzp.js   206.82 kB | gzip: 63.76 kB
    built in 293ms

Stale copy searches passed with no matches for previous non-role-aware navigation wording:

    rg -n "intentionally not enabled yet" ui\invomatch-ui\src
    rg -n "navigation is not role-aware" ui\invomatch-ui\src
    rg -n "fake frontend RBAC" ui\invomatch-ui\src
    rg -n "not role-aware yet" ui\invomatch-ui\src

Permission usage was verified in App.tsx and operational copy.

Backend/system validation was not rerun because no backend code or backend contracts were changed.

## Exit Criteria Check

- Admin Ops navigation uses backend-derived permissions only: satisfied.
- No frontend fake RBAC is introduced: satisfied.
- Unauthorized users do not see or enter Admin Ops from navigation: satisfied.
- Operational page still handles backend 401/403 safely: satisfied.
- Existing frontend flows remain available: satisfied.
- Frontend lint passes: satisfied.
- Frontend build passes: satisfied.
- Backend/system validation pack remains green if touched: not applicable; backend not touched.
- Closure doc added: satisfied by this document.
- Commit and push complete: satisfied after amended commit is pushed.
- Working tree clean: verified after push.

## Closure Decision

Mini-EPIC 31.8 is implementation-complete. Final repository closure is verified by amended commit, push, and clean working tree status.
