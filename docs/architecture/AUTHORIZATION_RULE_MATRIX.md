# Authorization Rule Matrix

## Purpose

Define the canonical authorization capability model and role-to-permission mapping for the current InvoMatch repository surface.

This matrix is the source of truth for permission evaluation.

It exists to ensure authorization is enforced consistently across:

- API routes
- backend services
- action execution
- export access
- current and future privileged operational capabilities

## Repository-Aligned Scope

The current repository exposes protected product capabilities for:

- input submission and input session lookup
- reconciliation run creation and run visibility
- review case visibility
- action execution
- direct export generation
- export artifact listing, metadata, and download

The repository also contains operational capabilities in backend services for:

- recovery evaluation
- retry / reentry handling
- startup repair
- operational metrics and audit visibility

The authorization model must therefore cover both current API surface and existing privileged backend capability surface.

## Authorization Design Rule

Authorization is capability-based.

Endpoints, UI controls, and handler names must not become independent policy sources.

Role checks should resolve into explicit permissions, and permission checks should be enforceable in backend services.

## Capability Set

The initial authorization capability set is:

- input.submit
- input.view
- runs.create
- runs.create_from_ingestion
- runs.list
- runs.read
- runs.read_view
- runs.read_review
- actions.resolve_review
- actions.export_run
- exports.download_direct
- artifacts.list
- artifacts.read_metadata
- artifacts.download
- operations.view_metrics
- operations.execute_recovery
- operations.execute_startup_repair
- operations.manage_admin_surface

## Capability Semantics

### input.submit

Allows submission of JSON or file input into the product ingestion boundary.

### input.view

Allows viewing input session details by input identifier.

### runs.create

Allows direct creation of a reconciliation run from CSV path inputs.

### runs.create_from_ingestion

Allows creation of a reconciliation run from accepted ingestion payloads.

### runs.list

Allows listing reconciliation runs.

### runs.read

Allows viewing a single reconciliation run detail.

### runs.read_view

Allows viewing the product run projection / unified run view.

### runs.read_review

Allows reading the product-facing review case for a run.

### actions.resolve_review

Allows execution of the resolve_review action when business-state guards also allow it.

This permission does not bypass lifecycle or action_guard rules.

### actions.export_run

Allows execution of the export_run action when business-state guards also allow it.

This permission does not bypass export eligibility or action_guard rules.

### exports.download_direct

Allows use of the direct export endpoint that creates an export artifact and returns export content immediately.

This is distinct from reading metadata or downloading an already-created artifact.

### artifacts.list

Allows listing export artifacts associated with a run.

### artifacts.read_metadata

Allows reading export artifact metadata by artifact identifier.

### artifacts.download

Allows downloading an already-created export artifact.

### operations.view_metrics

Allows access to privileged operational system visibility endpoints if or when exposed.

### operations.execute_recovery

Allows execution of privileged runtime recovery / retry / reentry control capabilities if or when exposed.

### operations.execute_startup_repair

Allows execution of privileged startup repair / restart consistency repair capabilities if or when exposed.

### operations.manage_admin_surface

Allows access to future admin-only security or system management endpoints.

## Role-to-Capability Matrix

### viewer

Allowed:

- input.view
- runs.list
- runs.read
- runs.read_view
- runs.read_review
- artifacts.list
- artifacts.read_metadata

Optional but not granted in the initial policy:

- artifacts.download

Denied:

- input.submit
- runs.create
- runs.create_from_ingestion
- actions.resolve_review
- actions.export_run
- exports.download_direct
- artifacts.download
- operations.view_metrics
- operations.execute_recovery
- operations.execute_startup_repair
- operations.manage_admin_surface

### operator

Allowed:

- input.submit
- input.view
- runs.create
- runs.create_from_ingestion
- runs.list
- runs.read
- runs.read_view
- runs.read_review
- actions.resolve_review
- actions.export_run
- exports.download_direct
- artifacts.list
- artifacts.read_metadata
- artifacts.download

Denied:

- operations.view_metrics
- operations.execute_recovery
- operations.execute_startup_repair
- operations.manage_admin_surface

### admin

Allowed:

- input.submit
- input.view
- runs.create
- runs.create_from_ingestion
- runs.list
- runs.read
- runs.read_view
- runs.read_review
- actions.resolve_review
- actions.export_run
- exports.download_direct
- artifacts.list
- artifacts.read_metadata
- artifacts.download
- operations.view_metrics
- operations.execute_recovery
- operations.execute_startup_repair
- operations.manage_admin_surface

## Important Distinctions

### Distinction 1: Authentication vs Authorization

Authentication proves who the user is.

Authorization decides what that authenticated user may do.

No protected capability may be granted based on authentication alone.

### Distinction 2: Visibility vs Mutation

Read-oriented permissions must remain distinct from state-changing permissions.

Examples:

- runs.read_review is not the same as actions.resolve_review
- artifacts.read_metadata is not the same as artifacts.download
- artifacts.download is not the same as actions.export_run
- actions.export_run is not the same as exports.download_direct

### Distinction 3: Permission vs Business-State Eligibility

Authorization approval does not override business-state rules.

Example:

- an operator may have actions.resolve_review permission
- but the action must still fail if the run is not in review_required state

Likewise:

- an operator may have actions.export_run permission
- but export must still fail if the run is not exportable

### Distinction 4: Route Access vs Handler Capability

A user may be allowed to access an endpoint surface while still being denied a specific action inside that surface.

This is especially important for:

- POST /api/reconciliation/runs/{run_id}/actions

The authorization layer must evaluate both:

- access to the action endpoint surface
- permission for the requested action type

## Default Deny Rule

Any capability not explicitly granted is denied.

Any new action type, privileged operation, or admin endpoint introduced after this matrix must be explicitly mapped before being considered authorized.

## Action Endpoint Rule

The action endpoint is not authorized as a single flat permission.

Requested action type must resolve to a specific capability.

Initial mapping:

- resolve_review -> actions.resolve_review
- export_run -> actions.export_run

Future action types must not inherit operator or admin permission automatically.

## Operational Capability Rule

Although operational recovery and repair are not yet fully exposed as public API routes, the repository already contains these capabilities in backend services.

They must be treated as privileged admin-only capabilities from this EPIC onward.

No operator permission should implicitly extend to:

- runtime recovery execution
- startup repair execution
- privileged operational control surfaces

## Service Enforcement Rule

Authorization must be enforceable beyond FastAPI route decorators.

The effective permission check must be available at service level for:

- action execution
- direct export generation
- artifact access
- operational repair / recovery actions

## Audit Rule

Permission decisions must be auditable for both allowed and denied outcomes.

At minimum, audit-relevant permission events should identify:

- user_id
- username
- role
- requested capability
- target resource type
- target resource id when available
- decision result
- denial reason when denied

## UI Rule

The UI may use this matrix to hide unavailable actions, but UI behavior is only advisory.

Backend authorization remains the source of truth.

## Validation Expectations

The matrix must be validated by tests that confirm:

- viewer cannot mutate product flow
- operator can perform normal product operations but not privileged admin operations
- admin can perform privileged actions
- action endpoint authorization matches action type
- business-state guards and permission guards both apply correctly
- denied permission outcomes are explicit and auditable