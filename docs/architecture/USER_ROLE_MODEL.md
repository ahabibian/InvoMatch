# User / Role Model

## Purpose

Define the minimal user and role model required to enforce a safe authentication and authorization boundary for the current InvoMatch product surface.

This model is intentionally minimal and does not introduce organization, tenant, team, or identity federation complexity.

## Design Constraints

The user and role model must be:

- explicit
- deterministic
- auditable
- easy to test
- safe for current single-product deployment
- expandable without rewriting product flow behavior

## User Model

The initial authenticated user model contains:

- user_id
- username
- role
- status
- auth_source
- created_at
- updated_at
- last_authenticated_at (when available)

## User Field Semantics

### user_id

Stable internal identifier for the authenticated principal.

Rules:

- must be unique
- must not be derived from UI labels
- must remain stable across permission checks and audit events

### username

Human-readable login identity or operator-facing identifier.

Rules:

- must be unique within the current security boundary
- used for traceability and audit readability
- not treated as the canonical identity key when user_id exists

### role

Primary authorization role assigned to the user.

The initial system supports a single effective role per user.

Multiple concurrent roles are out of scope for this EPIC.

### status

Lifecycle status for whether the known user may access protected system capabilities.

Supported values:

- active
- inactive

Rules:

- active users may proceed to authorization evaluation
- inactive users must be blocked from protected usage
- inactive users remain auditable as known identities

### auth_source

Indicates how the identity was authenticated.

Initial expected value:

- internal_token

This field exists to keep the model compatible with future auth provider expansion.

### created_at / updated_at

Audit-relevant timestamps for user record lifecycle.

### last_authenticated_at

Optional timestamp that may be updated when authentication succeeds.

Useful for audit and security visibility, but not required to complete permission decisions.

## Initial Role Model

The initial system defines three roles:

- viewer
- operator
- admin

These roles are intentionally coarse-grained.

They exist to protect the current product surface without introducing premature RBAC hierarchy complexity.

## Role Definitions

### viewer

Read-oriented user with visibility into product state, but without permission to mutate product flow.

Intended use:

- inspection
- status visibility
- run monitoring
- review visibility
- artifact visibility

Viewer must not be able to:

- submit input
- create runs
- resolve review
- trigger export generation
- execute privileged operational actions

### operator

Standard product operator role.

Intended use:

- submit input
- create and inspect runs
- resolve review decisions
- trigger export generation
- access normal product actions required for day-to-day workflow

Operator must not be able to:

- perform privileged recovery / repair actions
- access admin-only security or system management operations

### admin

Privileged system administrator role.

Intended use:

- all operator capabilities
- operational recovery and repair control
- access to privileged system-level actions
- future admin-only management endpoints

Admin exists because the repository already contains operational and repair capabilities that should not be exposed to normal operators once external trust boundaries exist.

## Role Simplicity Rule

Roles are the coarse-grained identity layer.

Permissions are the fine-grained enforcement layer.

The system must not rely on role names directly inside product logic when a permission check is more appropriate.

Role-to-permission mapping belongs to authorization policy, not to product flow logic itself.

## Status Model

Supported user statuses:

- active
- inactive

No additional status hierarchy is introduced in this EPIC.

The following are explicitly out of scope:

- invited
- suspended
- locked
- pending_password_reset
- soft_deleted
- federated_only

These can be added later if real product requirements appear.

## Effective Access Rule

A user may access a protected capability only when both conditions are true:

1. the user is authenticated
2. the user status is active

Passing those checks does not automatically grant action permission.

Role and permission evaluation must still occur after authentication and status validation.

## Audit Requirements for User / Role State

Authorization-relevant audit records should be able to identify:

- user_id
- username
- role
- status
- auth_source
- attempted capability or endpoint
- decision outcome

This ensures denied and privileged actions remain explainable.

## Repository-Aligned Security Boundary

The current repository exposes product-facing routes for:

- input submission and lookup
- run creation and visibility
- review visibility
- action execution
- export generation
- export artifact access

It also contains operational recovery and repair services.

Therefore the role model must cover both:

- current public product routes
- existing privileged backend operational capabilities

## Out of Scope for This Model

This EPIC does not introduce:

- organization membership
- tenant membership
- project-scoped roles
- dynamic custom roles
- nested RBAC hierarchy
- policy editing UI
- delegated impersonation
- approval chains

## Implementation Direction

Implementation should introduce explicit security-domain models for:

- user identity
- role enumeration
- user status enumeration
- authenticated principal / auth context

These models must be independent from UI concerns and reusable across route and service enforcement.

## Validation Expectations

The user and role model must be validated by tests that confirm:

- active vs inactive access behavior
- viewer / operator / admin distinction
- role-to-permission consistency
- audit visibility of identity and role decisions