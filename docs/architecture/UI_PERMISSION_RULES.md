# UI Permission Rules

## Purpose

Define how the minimal InvoMatch UI must consume backend authorization policy without becoming a second source of truth.

The UI must reflect permission boundaries clearly, but backend authorization remains authoritative.

## Core Rule

The UI is a permission-aware surface, not a permission authority.

It may:

- hide unavailable actions
- disable unavailable controls
- block navigation to unauthorized screens
- display explicit permission-denied states

It must not:

- grant access based on UI state alone
- assume hidden controls are sufficient protection
- bypass backend authorization
- define its own independent permission policy

## Policy Source Rule

The UI must derive permission behavior from the backend authorization model.

It must not invent role meanings or capability rules locally.

The backend remains the source of truth for:

- authenticated identity
- effective role
- allowed capabilities
- final allow / deny decision

## UI Capability Consumption

The UI should consume permission-relevant information in a form suitable for rendering, such as:

- authenticated user identity
- current role
- capability flags
- permission-denied responses from backend

The UI must not hardcode business authorization logic beyond simple presentation behavior.

## Screen and Action Rules

### Input Submission UI

Visible and usable for:

- operator
- admin

Not available for:

- viewer

Expected UI behavior for viewer:

- upload or submit controls hidden or disabled
- direct navigation attempts handled gracefully
- backend denial still enforced if request is attempted outside normal UI flow

### Run Listing and Run Detail UI

Visible for:

- viewer
- operator
- admin

The UI may display run state and product detail to all authenticated roles that hold the corresponding read permissions.

### Review Visibility UI

Visible for:

- viewer
- operator
- admin

The UI may display review status and review case detail for authorized read roles.

### Review Resolution UI

Visible and usable for:

- operator
- admin

Not available for:

- viewer

Rules:

- viewer must not be shown active review-decision controls
- operator and admin may see decision controls only when the backend indicates the action is permitted by both permission and business state
- UI must tolerate backend conflict responses if state changes after rendering

### Direct Export UI

Visible and usable for:

- operator
- admin

Not available for:

- viewer

Rules:

- direct export trigger must not be presented as a viewer capability
- export failure or non-exportable states must be surfaced clearly
- permission allow does not imply business-state eligibility

### Export Artifact Listing UI

Visible for:

- viewer
- operator
- admin

Rules:

- artifact list and metadata visibility may be shown for read-authorized roles
- artifact download controls must follow artifact download permission, not merely metadata visibility

### Artifact Download UI

Visible and usable for:

- operator
- admin

Not available for:

- viewer

Rules:

- viewer may see artifact existence but must not see active download controls in the initial policy
- backend remains authoritative if UI state is stale or bypassed

## Unauthorized Navigation Rule

If a user attempts to access a screen or route they are not allowed to use, the UI must:

- prevent normal access when permission information is available
- display a clear not-authorized state
- avoid broken or blank screens
- avoid pretending the data does not exist when the actual issue is permission denial

## Backend Error Handling Rule

The UI must distinguish clearly between:

- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
- 409 Conflict
- other business or server errors

Expected handling:

### 401 Unauthorized

Interpretation:

- user is not authenticated
- token is missing, expired, or invalid

UI behavior:

- show authentication-required state
- redirect to login boundary when implemented
- avoid showing stale privileged UI as if session were still valid

### 403 Forbidden

Interpretation:

- user is authenticated but lacks permission or is inactive

UI behavior:

- show explicit permission-denied message
- do not mislabel as missing data
- keep the denial understandable and non-technical where possible

### 404 Not Found

Interpretation:

- target resource genuinely not found

UI behavior:

- show not-found state

### 409 Conflict

Interpretation:

- user is authorized, but action conflicts with current business state

UI behavior:

- show action conflict or stale-state message
- refresh or re-query affected state when appropriate

## UI State Freshness Rule

The UI must assume permission and business-state information can become stale.

Therefore:

- hidden controls are advisory
- disabled actions may still require backend confirmation
- action submission responses must always be interpreted as final

This is especially important for:

- review resolution
- export triggering
- artifact download availability

## Minimal Rendering Guidance

The UI should present permission differences in a controlled way:

- hide clearly unavailable primary actions
- disable borderline actions when helpful
- show explanatory text when the user can see context but cannot act
- prefer clarity over silent disappearance when the user expects an action

## No Second Policy Rule

The UI must not maintain a separate authorization matrix that can drift from backend policy.

Any frontend mapping must be derived from backend-provided identity or capability information and validated by integration tests.

## Audit-Relevant UI Behavior

The UI itself is not the audit source of truth, but it should avoid obscuring security-relevant outcomes.

Important examples:

- permission-denied responses should remain visible to the operator
- failed privileged action attempts should not be silently swallowed
- session expiration should not appear as random application failure

## Validation Expectations

UI permission behavior must be validated by tests that confirm:

- unavailable actions are not shown to unauthorized roles
- unauthorized navigation is blocked gracefully
- backend 401 and 403 responses are surfaced correctly
- review resolution visibility matches backend permission policy
- export and artifact download visibility align with backend authorization
- UI cannot turn unauthorized operations into successful backend calls