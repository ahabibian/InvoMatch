
Real Package Creation Procedure
Status

Procedure defined.

This document defines the governed real package creation procedure for EPIC 32.

It does not create a package.

It does not create a real release manifest.

It does not publish artifacts.

It does not approve deployment.

It does not authorize CI release behavior.

It does not promote any environment.

It does not modify finalized evidence.

It does not silently mutate prior evidence.

It does not approve release execution.

Purpose

The purpose of this procedure is to define how a future real package creation step must be executed deterministically, traceably, and safely.

Package creation is a governed release pipeline step. It is not deployment. It is not publication. It is not environment promotion. It is not release execution.

A package may only be created after an explicit package creation authorization decision record exists and remains valid.

Governance Context

Mini-EPIC 32.75 created the real package creation authorization decision record.

Mini-EPIC 32.76 defines the controlled procedure that must be followed before any real package creation occurs.

This procedure exists to prevent the release pipeline from drifting from governance into uncontrolled execution.

Required Starting State

Before real package creation may begin, the operator must confirm all of the following:

The repository is on the intended release branch.
The working tree is clean.
The current commit is the exact source commit intended for package creation.
The package creation authorization decision record exists.
The authorization decision record explicitly authorizes package creation as the next governed step.
The authorization decision record does not authorize deployment, publication, CI release behavior, or environment promotion.
Finalized evidence is not modified.
Prior evidence is not silently mutated.
The package creation procedure has been reviewed before execution.
The package output location is local, controlled, and non-public.

If any required starting state condition is false, package creation must be blocked.

Source Identity Requirements

A real package must record source identity before any package output is produced.

The required source identity fields are:

source_branch
source_commit_sha
source_commit_short_sha
working_tree_clean
package_created_from_clean_tree
package_created_by_operator
package_created_at_utc
package_creation_authorization_reference
package_creation_procedure_reference

The source commit SHA must be obtained from Git at package creation time.

The working tree state must be checked immediately before package creation.

A package must not be created from a dirty working tree.

A package must not be created from an unknown commit.

A package must not be created from untracked, unstaged, or partially staged source changes.

Package Identity Requirements

A real package must have a deterministic and traceable package identity.

The required package identity fields are:

package_schema_version
package_name
package_type
package_status
package_created_at_utc
package_source_commit_sha
package_source_branch
package_authorization_decision
package_procedure_reference
package_local_path
package_publication_status

The package_status must not claim deployment readiness.

The package_publication_status must be local-only unless a separate future publication authorization exists.

The package identity must not imply that the package has been deployed, released, published, promoted, or approved for production.

Manifest Requirements

A real package must include or be accompanied by a real package manifest.

The real package manifest must be separate from the dry-run preview manifest.

The real package manifest must not reuse dry-run-only status fields in a way that creates ambiguity.

The real package manifest must include:

schema_version
dry_run flag set to false
package_status
package_identity
source_identity
evidence_reference
included_components
excluded_components
validation_summary
non_deployment_boundary
operator_responsibility
rollback_boundary
blocked_actions

The manifest must be JSON-serializable.

The manifest must be deterministic enough to support review and audit.

The manifest must not include secrets.

The manifest must not include local runtime databases unless explicitly authorized by a later governed decision.

The manifest must not include dependency caches.

The manifest must not include public release objects unless explicitly authorized by a later governed decision.

Evidence Reference Requirements

A real package manifest may reference evidence.

It must not modify finalized evidence.

It must not silently mutate prior evidence.

It must not claim that referenced evidence was newly executed unless the execution actually occurred and is separately recorded.

Evidence references must include document paths and relevant governance records.

Required evidence references include:

EPIC 32 release pipeline document
package creation authorization decision record
real package creation procedure
release candidate evidence index, if applicable
finalized evidence decision record, if applicable
package-related closure record

Evidence reference inclusion does not mean the evidence is embedded in the package unless the manifest explicitly states it.

Included Components

The future real package creation step may include only controlled project artifacts needed to represent the source package.

Allowed package components may include:

source files required for the application
backend source code under src
backend tests if the package type requires validation reproducibility
frontend source code under ui/invomatch-ui
relevant project configuration files
architecture documentation needed for release traceability
package manifest
package creation metadata

The exact included component list must be recorded in the real package manifest.

No component may be included implicitly.

Excluded Components

The real package must exclude:

local runtime databases
local temporary folders
dependency caches
.pytest_tmp
node_modules
Python virtual environments
build caches
local preview outputs
dry-run preview outputs unless explicitly referenced as historical context
secrets
credentials
personal tokens
environment files containing secrets
public release objects
deployment credentials
production environment state
generated artifacts not explicitly allowed by the manifest
unrelated working files

The excluded component list must be recorded in the real package manifest.

Dry-Run to Real Manifest Separation

The package manifest dry-run system exists only as a preview and validation mechanism.

A dry-run preview manifest must not be treated as a real package manifest.

A real package manifest must use real package creation metadata.

A real package manifest must have dry_run set to false.

A real package manifest must not inherit preview-only claims.

A real package manifest must not claim that a package was created before the package creation operation actually occurs.

The future package creation step must maintain a clear separation between:

dry-run preview
real manifest
real package archive or package directory
publication artifact
deployment artifact

Only the first three may be considered during real package creation unless a later governed decision authorizes publication or deployment.

Validation Steps Before Package Creation

Before package creation, the operator must run the required validation checks for the intended package creation step.

At minimum, the operator must verify:

Current branch.
Current commit SHA.
Clean working tree.
Presence of authorization decision record.
Presence of this procedure.
No finalized evidence mutation.
No prior evidence silent mutation.
No package output already exists at the intended target path unless replacement is explicitly controlled.
No blocked action is being performed.
Package creation output path is local and non-public.

The future implementation may add automated validation scripts, but automated validation must not weaken this procedure.

Validation Steps After Package Creation

After a future package is created, the operator must verify:

The package exists only in the intended local package output path.
The real package manifest exists.
The manifest dry_run field is false.
The manifest source commit matches the Git commit used for package creation.
The manifest branch matches the intended branch.
The manifest records the clean working tree requirement.
The manifest records included components.
The manifest records excluded components.
The manifest records the non-deployment boundary.
The manifest records blocked actions.
The package is not published.
No deployment action occurred.
No CI release behavior was triggered.
No environment was promoted.
Finalized evidence was not modified.

If any post-creation validation fails, the package must be considered invalid and must not be used for publication or deployment.

Operator Responsibility

The operator is responsible for confirming that package creation follows this procedure exactly.

The operator must not rely on package creation as proof of release readiness.

The operator must not treat a package as a deployment artifact unless a later governed decision explicitly authorizes that transition.

The operator must preserve traceability from:

authorization decision
procedure
source commit
package manifest
package output
closure record

The operator must stop the process if any governance boundary is unclear.

Rollback and Non-Publication Boundary

Real package creation is local and reversible until a separate publication step is authorized.

If a package is created incorrectly, the invalid local package output may be deleted or superseded by a corrected package creation attempt.

Any correction must be recorded.

Invalid package output must not be published.

Invalid package output must not be deployed.

Invalid package output must not be used as release evidence without a correction or supersession record.

Package creation does not imply publication.

Package creation does not imply deployment.

Package creation does not imply environment promotion.

Package creation does not imply customer availability.

Blocked Actions

The following actions are blocked by this procedure:

creating a package during Mini-EPIC 32.76
creating a real release manifest during Mini-EPIC 32.76
publishing artifacts
creating GitHub releases
creating public release assets
pushing package artifacts to public storage
deploying to any environment
promoting staging or production
modifying finalized evidence
silently mutating prior evidence
authorizing CI release behavior
executing release automation
claiming release-candidate readiness unless separately approved
claiming deployment readiness
claiming production readiness

Any blocked action requires a separate future governed mini-epic and explicit authorization.

Exit Criteria for This Procedure Definition

Mini-EPIC 32.76 may close only when:

This real package creation procedure exists.
The procedure explicitly preserves all non-deployment boundaries.
The procedure explicitly separates dry-run preview manifests from real package manifests.
The procedure defines required source identity fields.
The procedure defines required package identity fields.
The procedure defines manifest requirements.
The procedure defines evidence reference requirements.
The procedure defines included and excluded component expectations.
The procedure defines validation steps before package creation.
The procedure defines validation steps after package creation.
The procedure defines operator responsibility.
The procedure defines rollback and non-publication boundaries.
The procedure defines blocked actions.
The EPIC 32 summary references this procedure.
No package has been created.
No real release manifest has been created.
No artifact has been published.
No deployment has been approved.
No environment has been promoted.
Final Boundary Statement

This document defines the governed real package creation procedure only.

It does not create packages.

It does not create real release manifests.

It does not publish artifacts.

It does not approve deployment.

It does not authorize CI release behavior.

It does not promote any environment.

It does not modify finalized evidence.

It does not silently mutate prior evidence.

It does not approve release execution.
