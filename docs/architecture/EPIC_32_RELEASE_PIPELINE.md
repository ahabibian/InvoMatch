# EPIC 32 - DevOps & Release Pipeline

## Status

In progress.

## Context

EPIC 31 is closed.

The system now provides:

- deterministic end-to-end execution
- tenant-aware isolation
- security-hardened trust boundaries
- restart-safe persistence and recovery
- operational monitoring and visibility
- auditability and traceability
- deployment-ready runtime behavior
- usable operator-facing workflows

The system is operationally mature, but release management is still manual and fragile.

A production-grade system is not ready because it can be deployed once. It is ready when it can be deployed safely, repeatedly, and predictably.

EPIC 32 introduces release discipline, validation gates, deployment verification rules, promotion safety, rollback awareness, and release traceability without introducing unnecessary infrastructure complexity.

## Objective

Introduce a repeatable and reliable release pipeline so InvoMatch can move safely through:

development -> validation -> staging -> production

After this EPIC, the system must support:

- automated validation before release
- reproducible builds
- environment-aware deployment flow
- controlled release discipline
- deployment verification
- rollback-aware failure handling
- release traceability

## Non-Goals

EPIC 32 does not include:

- Kubernetes orchestration
- autoscaling
- multi-region deployment
- infrastructure-as-code platforms
- advanced cloud-native tooling
- enterprise CI/CD complexity

This EPIC is about reliable release execution, not infrastructure overengineering.

## Mini-EPIC 32.0 Baseline Finding

Before formalizing release gates, the backend full test baseline exposed test drift caused by newer finalized projection invariants.

Initial backend full baseline result:

8 failed, 680 passed

The failures were caused by older tests that still constructed completed runs without finalized projection stores or readable finalized projections.

This violated the current production invariant:

A completed run must have a finalized projection that can be read back safely.

The product scenario pack was already green, but the full backend test baseline was not.

Mini-EPIC 32.0 therefore included release-baseline test drift repair before documenting the release contract.

After repair:

688 passed

This confirms that the release baseline must include the full backend test pack, not only selected scenario tests.

## Release Validation Layers

Every release candidate must pass the following validation layers.

### 1. Required Scenario Regression Pack

Purpose:

Protect the most important production flows touched by release, startup, recovery, health, monitoring, and deployment behavior.

Command:

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"

    pytest -q `
      tests\system\test_happy_path_full_flow.py `
      tests\system\test_runtime_failure_terminalization.py `
      tests\system\test_restart_recovery_consistency.py `
      tests\system\test_startup_repair_visibility_recovery_alignment.py `
      tests\test_health.py `
      tests\test_health_readiness.py `
      tests\operational\test_operations_metrics_api.py `
      --basetemp=.pytest_tmp

Current baseline result:

29 passed

### 2. Operational Validation Pack

Purpose:

Validate operational metrics, health summaries, alerts, recovery loop observability, startup repair observability, scheduler behavior, condition detection, and retry/recovery policies.

Command:

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"

    pytest -q tests\operational --basetemp=.pytest_tmp

Current baseline result:

78 passed

### 3. Contract Validation Pack

Purpose:

Protect product-facing API response shapes and prevent internal field leakage.

Command:

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"

    pytest -q tests\contracts --basetemp=.pytest_tmp

Current baseline result:

10 passed

### 4. Full Backend Validation Pack

Purpose:

Validate the full backend regression baseline.

Command:

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"

    pytest -q tests --basetemp=.pytest_tmp

Current baseline result:

688 passed

### 5. Frontend Lint

Purpose:

Validate frontend source quality and static lint rules.

Command:

    cd C:\dev\InvoMatch\ui\invomatch-ui

    npm run lint

Current baseline result:

eslint completed with no reported errors.

### 6. Frontend Build

Purpose:

Validate TypeScript compilation and production bundle creation.

Command:

    cd C:\dev\InvoMatch\ui\invomatch-ui

    npm run build

Current baseline result:

tsc -b and vite build completed successfully.
Vite transformed 28 modules.
Build completed in 549ms.

## Required Scenario Mapping

| Scenario | Purpose | Test Coverage |
|---|---|---|
| Scenario 1 - Happy Path Full Flow | Validates upload/run/review/export-ready product flow | tests\system\test_happy_path_full_flow.py |
| Scenario 4 - Runtime Failure Terminalization | Validates failed runtime terminalization and blocked export readiness | tests\system\test_runtime_failure_terminalization.py |
| Scenario 6 - Restart Recovery Consistency | Validates restart-safe persisted state recovery | tests\system\test_restart_recovery_consistency.py |
| Scenario 7 - Startup Repair Visibility & Recovery Alignment | Validates startup repair, readiness, health, and recovery alignment | tests\system\test_startup_repair_visibility_recovery_alignment.py |
| Scenario 13 - Monitoring & Health Visibility Integrity | Validates health/readiness and operational monitoring surfaces | tests\test_health.py, tests\test_health_readiness.py, tests\operational\test_operations_metrics_api.py, tests\operational |

## Scenario 13 Status

Scenario 13 is currently represented by health, readiness, operational API, and operational visibility tests rather than a single dedicated system scenario file.

This is acceptable for Mini-EPIC 32.0 because the coverage exists and is release-blocking.

A later Mini-EPIC may consolidate this into a dedicated system scenario file:

tests\system\test_monitoring_health_visibility_integrity.py

## Release Gate Rules

A release candidate is valid only if all mandatory validation layers pass.

A release candidate must be rejected if:

- any required scenario regression fails
- any contract test fails
- any operational validation test fails
- the full backend test pack fails
- frontend lint fails
- frontend build fails
- environment configuration is incomplete or unsafe
- startup validation fails
- release identity cannot be traced to a commit
- deployment verification cannot confirm health/readiness

No release may be promoted based only on partial test success.

## Current Reproducibility Risk

The backend dependency model is not fully reproducible yet.

Current pyproject.toml uses unpinned dependencies:

- fastapi
- uvicorn
- pydantic
- pytest
- python-multipart

This means dependency resolution may change over time.

This is acceptable as a documented limitation for Mini-EPIC 32.0, but later EPIC 32 work must introduce dependency locking or pinned release constraints before production release discipline can be considered complete.

The frontend has npm-based installation behavior, but release packaging still needs to define deterministic install rules.

## Environment Promotion Model

The intended promotion flow is:

development -> validation -> staging -> production

Promotion rules:

1. Development may run partial checks during local work.
2. Validation must run the full release validation pack.
3. Staging must use production-like configuration without production data.
4. Production promotion must occur only after staging validation succeeds.
5. No environment may share mutable runtime state with another environment.
6. Production debug behavior must remain disabled.
7. Startup validation must pass after deployment.
8. Release identity must be recorded.

## Deployment Verification Rules

After deployment, the system must verify:

- application startup succeeds
- /health responds correctly
- /readiness responds correctly
- startup repair result is visible
- operational health summary is available to authorized admin users
- persistence paths are available
- finalized projection store is available
- recovery loop startup does not silently fail
- monitoring and operational visibility surfaces are not broken

## Rollback and Failure Handling Rules

A failed deployment must not remain hidden.

Rollback-safe behavior requires:

- failed startup prevents promotion
- invalid configuration rejects deployment
- failed migrations or persistence initialization block release
- readiness failure prevents production promotion
- operational visibility exposes failure state
- release metadata identifies the failed version
- rollback restores the last known valid release state

Mini-EPIC 32.0 documents these rules but does not yet automate rollback.

## Release Traceability Model

Every release must be traceable to:

- release version
- deployed git commit
- deployment timestamp
- target environment
- validation result
- operator or automation identity
- rollback status if applicable

This model must align with the existing audit and operational visibility direction.


---

## Release Identity and Version Metadata Foundation

Mini-EPIC 32.5 introduces the first minimal release identity foundation for InvoMatch.

This foundation does not create a public release, deployment, tag, package, artifact, staging promotion, production promotion, changelog, or rollback implementation.

Its purpose is narrower and stricter:

- every future validated release candidate must be traceable to a stable runtime identity;
- runtime identity must be product-safe and operationally visible;
- missing release metadata must be explicit instead of silently fabricated;
- release validation status must not be claimed by runtime unless release tooling explicitly provides it.

### Release Identity Model

The release identity model contains the following fields:

| Field | Meaning |
|---|---|
| `application_name` | Stable application identifier. Current default: `invomatch`. |
| `application_version` | Application/internal release version. Current default: `0.1.0` from the backend project baseline. |
| `git_commit_sha` | Commit SHA associated with the runtime when provided by release/build tooling. Falls back to `unknown`. |
| `git_branch` | Branch or ref associated with the runtime when provided by release/build tooling. Falls back to `unknown`. |
| `build_timestamp_utc` | UTC build timestamp when provided by release/build tooling. Falls back to `null`. |
| `environment` | Configured InvoMatch runtime environment. |
| `validation_status` | Explicit validation status from release tooling. Falls back to `not_declared`. |
| `metadata_available` | `true` only when concrete commit and branch metadata are both available. |

### Runtime Boundary

Release identity is exposed as operational metadata through:

    GET /api/operations/release-identity

This endpoint is protected by the existing operational permission boundary:

    operations.view_metrics

The endpoint is intentionally placed under `/api/operations` instead of `/health` or `/readiness`.

Health and readiness endpoints must remain runtime state checks. They must not become release audit surfaces.

### Environment Variable Boundary

The release identity service reads only the following allow-listed environment variables:

| Environment Variable | Purpose |
|---|---|
| `INVOMATCH_APPLICATION_NAME` | Optional application name override. |
| `INVOMATCH_APPLICATION_VERSION` | Optional application version override. |
| `INVOMATCH_RELEASE_COMMIT_SHA` | Optional release/build commit SHA. |
| `INVOMATCH_RELEASE_BRANCH` | Optional release/build branch or ref. |
| `INVOMATCH_RELEASE_BUILD_TIMESTAMP_UTC` | Optional UTC build timestamp. |
| `INVOMATCH_RELEASE_VALIDATION_STATUS` | Optional validation status explicitly injected by release tooling. |

No arbitrary environment variables are exposed.

Secrets, token configuration, persistence paths, storage paths, seed token JSON, and CI internals must not appear in release identity output.

### Validation Status Boundary

`validation_status` is not proof that CI passed unless release tooling explicitly injects a value after validation.

The default value is:

    not_declared

This is intentional.

Runtime must not infer release-candidate readiness merely because the application starts, health passes, readiness passes, or local tests previously passed.

A release-candidate-ready decision still requires the release validation pack and GitHub Actions evidence defined elsewhere in this document.

### Missing Metadata Behavior

When release metadata is absent, the service must fall back safely:

| Missing Input | Runtime Output |
|---|---|
| missing commit SHA | `git_commit_sha = "unknown"` |
| missing branch/ref | `git_branch = "unknown"` |
| missing build timestamp | `build_timestamp_utc = null` |
| missing validation status | `validation_status = "not_declared"` |
| missing commit or branch | `metadata_available = false` |

This prevents the system from lying about release traceability.

### Non-Goals

Mini-EPIC 32.5 does not introduce:

- Docker packaging
- deployment
- staging environment
- production environment
- semantic version tag creation
- GitHub Release creation
- changelog generation
- artifact publishing
- rollback implementation
- environment promotion automation
- CI matrix expansion
- frontend UI changes
- release validation gate changes

## Build and Packaging Rules

Release packaging must eventually ensure:

- deterministic backend dependency installation
- deterministic frontend dependency installation
- versioned build artifacts
- stable startup behavior across environments
- explicit environment configuration
- no hidden local-only runtime assumptions

Mini-EPIC 32.0 does not implement packaging automation. It defines the validation baseline that packaging work must obey.

## Implementation Plan

### Phase 1 - Baseline Inspection

- inspect repository test surface
- identify scenario files
- identify operational tests
- identify contract tests
- inspect frontend scripts
- inspect dependency model

### Phase 2 - Test Drift Repair

- run full backend baseline
- identify release-blocking failures
- repair old tests to respect finalized projection invariants
- ensure no production invariant is weakened

### Phase 3 - Validation Baseline

- run required scenario regression pack
- run operational validation pack
- run contract validation pack
- run full backend validation pack
- run frontend lint
- run frontend build

### Phase 4 - Documentation

- document release gate rules
- document validation commands
- document scenario mapping
- document reproducibility risks
- document closure evidence

### Phase 5 - Future CI Migration

- convert manual validation pack into CI workflow
- preserve the same gates
- fail clearly on any regression
- avoid adding CI steps that are not already locally reproducible

## Test Strategy

EPIC 32 validation starts with manual PowerShell-first commands.

This is intentional.

The release contract must be clear and locally reproducible before automation is introduced.

CI should automate this contract later; it should not define the contract implicitly.

## Closure Criteria for Mini-EPIC 32.0

Mini-EPIC 32.0 is complete only if:

- EPIC 32 release pipeline architecture document exists
- release validation layers are documented
- required scenario regression pack is mapped to concrete test files
- release gate rules are documented
- environment promotion model is documented
- deployment verification rules are documented
- rollback/failure handling rules are documented
- release traceability model is documented
- current reproducibility limitations are documented
- backend full baseline passes
- operational validation passes
- contract validation passes
- frontend lint passes
- frontend build passes
- closure document is created
- all changes are committed

## CI Release-Gate Evidence Model

EPIC 32 treats GitHub Actions CI validation as release-gate evidence, not merely as a convenience check.

A green CI run means that the configured release validation baseline passed on a specific commit. A red CI run blocks release-related closure until the failure is understood, repaired if necessary, and followed by a final passing CI run.

### Release-Blocking CI Steps

The following CI steps are release-blocking:

| CI Step | Release-Gate Meaning |
|---|---|
| Backend full test baseline | Backend regression surface must pass on GitHub Actions. |
| Contract tests | API and boundary contracts must remain stable. |
| Operational tests | Operational visibility and repair behavior must remain valid. |
| Required scenario regression pack | Critical end-to-end product scenarios must remain valid. |
| Frontend lint | Frontend code must pass configured lint rules. |
| Frontend build | Frontend production build must compile successfully. |

Any failed release-blocking step blocks release closure.

Warnings do not block release closure unless they affect runtime behavior, security, future compatibility, deployment safety, validation reliability, or evidence trustworthiness.

### Required CI Evidence For Release-Related EPIC Closure

Release-related EPIC closure must capture:

| Evidence Field | Required |
|---|---|
| Workflow name | Yes |
| GitHub Actions run number | Yes |
| Commit SHA | Yes |
| Branch | Yes |
| Status | Yes |
| Duration | Yes, if available |
| Failed step | Required for failed runs |
| Failure reason | Required for failed runs |
| Repair commit | Required if a repair was made |
| Final passing run | Required after any failed run |
| Local validation command(s) | Required when local validation is used as supporting evidence |
| CI/local drift note | Required if CI and local behavior differed |

### Mini-EPIC 32.1 CI Evidence Captured

| Evidence | Value |
|---|---|
| Initial CI run | #153 |
| Initial commit | 9ddc8b0 |
| Initial status | Failed |
| Failure reason | Missing `.pytest_tmp` parent directory on a clean GitHub Actions runner. |
| Release-gate result | Blocked until repaired. |
| Repair commit | 6e0cce0 |
| Repair commit message | ci: prepare pytest temp root in validation workflow |
| Final CI run | #154 |
| Final commit | 6e0cce0 |
| Final status | Passed |
| Release-gate result | CI validation baseline became usable as release evidence. |

### CI/Local Drift Rule

If local validation passes but CI fails, CI is treated as the release-gate source of truth for closure.

The drift must be investigated, repaired, committed, pushed, and validated by a final passing GitHub Actions run before release-related closure.

---

## Release Candidate Validation Pack

A commit may be considered **release-candidate-ready** only after both local validation and GitHub Actions validation evidence have been reviewed and recorded.

Release-candidate-ready does not mean deployed, packaged, tagged, published, promoted to staging, or promoted to production. It only means the commit has passed the agreed validation gate and is eligible for a later release/deployment process.

### Required Local Validation Pack

The local validation pack must be run from a clean working tree unless the operator is explicitly validating uncommitted documentation changes before commit.

Required commands:

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"
    pytest -q --basetemp=.pytest_tmp

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"
    pytest -q tests\contracts --basetemp=.pytest_tmp

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"
    pytest -q tests\operational --basetemp=.pytest_tmp

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"
    pytest -q tests\system\test_happy_path_full_flow.py tests\system\test_review_resolution_flow.py tests\system\test_runtime_failure_terminalization.py tests\system\test_startup_repair_visibility_recovery_alignment.py --basetemp=.pytest_tmp

    cd C:\dev\InvoMatch\ui\invomatch-ui
    npm run lint
    npm run build

If a listed test directory does not exist in the current repository state, the operator must record that fact explicitly instead of silently skipping the validation category. The current repository contract validation path is tests\contracts.

### Required Local Evidence

For each local validation command, the release candidate evidence must include:

- command
- result
- pass/fail status
- test count or build/lint result when available
- failure summary if failed
- repair commit if a repair was needed
- final passing command result after repair

### Required GitHub Actions Evidence

The GitHub Actions validation evidence must include:

- workflow name
- run number
- commit SHA
- branch
- status
- failed step, if any
- repair commit, if any
- final passing run number
- final passing commit SHA

A red GitHub Actions run blocks release-candidate readiness. A later local pass does not override a red CI run. The defect or drift must be repaired, pushed, and validated again by GitHub Actions.

### Manual Release Candidate Checklist

Before declaring a commit release-candidate-ready, the operator must confirm:

| Check | Required Evidence |
|---|---|
| Working tree clean before final validation | `git status` output |
| Branch aligned with origin | `git status` output |
| Backend full test baseline passed | `pytest -q --basetemp=.pytest_tmp` result |
| Contract/API validation passed or absence recorded | command result |
| Operational validation passed | `pytest -q tests\operational --basetemp=.pytest_tmp` result |
| Scenario regression pack passed | listed system test command result |
| Frontend lint passed | `npm run lint` result |
| Frontend build passed | `npm run build` result |
| GitHub Actions run reviewed | workflow name, run number, commit SHA, branch, status |
| Any red CI run repaired | repair commit and final passing run |
| Release-candidate-ready is not described as deployed/released | documentation wording review |
| Closure document created | Mini-EPIC closure file path |
| Documentation committed | commit SHA |
| Documentation pushed | `git push origin main` result |

### Release Candidate Boundary

The following states are explicitly outside release-candidate validation:

- deployed
- packaged
- Dockerized
- tagged
- published
- promoted to staging
- promoted to production
- rollback-ready
- changelog-published

Those activities require later EPIC 32 mini-epics or a dedicated release/deployment epic.

## Mini-EPIC 32.6 - CI Release Metadata Injection Boundary

Mini-EPIC 32.6 connects the release identity metadata foundation to the CI validation workflow without creating a release, tag, package, deployment, or promotion mechanism.

### CI Metadata Injection

The CI validation workflow may inject only bounded, product-safe release identity metadata:

| Environment variable | CI value | Purpose |
|---|---|---|
| `INVOMATCH_RELEASE_COMMIT_SHA` | `${{ github.sha }}` | Identifies the exact commit being validated. |
| `INVOMATCH_RELEASE_BRANCH` | `${{ github.ref_name }}` | Identifies the branch or ref name under validation. |
| `INVOMATCH_RELEASE_VALIDATION_STATUS` | `not_declared` | Prevents runtime from claiming release readiness. |

### Intentionally Not Injected

`INVOMATCH_RELEASE_BUILD_TIMESTAMP_UTC` is intentionally not injected by the current CI workflow.

The current workflow does not provide a deterministic UTC build timestamp value that should be treated as release identity. A future release packaging or artifact creation step may inject a real build timestamp when packaging exists.

### Validation Status Boundary

Runtime release identity must not claim that a build is release-candidate-ready merely because CI is currently running.

`validation_status` remains `not_declared` during CI validation. The actual release gate remains the external CI evidence:

- backend full validation;
- contract/API validation;
- operational validation;
- required scenario regression pack;
- frontend lint;
- frontend build.

A future release promotion step may set a stronger validation status only after validation evidence has completed and been captured. Mini-EPIC 32.6 does not add that promotion step.

### Non-Release Boundary

Mini-EPIC 32.6 does not create or modify:

- semantic version tags;
- GitHub Releases;
- Docker images;
- release packages;
- deployment environments;
- staging or production promotion;
- changelog generation;
- rollback automation;
- frontend release UI.

## Mini-EPIC 32.7 - Release Candidate Evidence Index & Validation Run Traceability

Mini-EPIC 32.7 defines a documentation-first release candidate evidence index boundary.

The purpose is to record which validation evidence belongs to a given release candidate validation run without creating a package, deployment, semantic version tag, GitHub Release, public artifact, promotion event, rollback point, changelog, or runtime release registry.

### Architecture Decision

Release candidate validation evidence is represented as a documentation artifact.

The evidence index records:

- commit SHA
- branch/ref
- validation date/time as documented evidence
- validation source (`local`, `ci`, `mixed`, or `documented`)
- validation command groups
- result summaries
- related closure documents
- related evidence files or logs

The validation date/time is not runtime truth.

It is not a build timestamp unless a future build process explicitly produces it.

The evidence index does not claim production release readiness.

### Evidence Index Boundary

The format is defined in:

    docs/architecture/RELEASE_CANDIDATE_EVIDENCE_INDEX.md

Recommended future index location:

    docs/architecture/evidence/release_candidates/

Recommended future naming pattern:

    RC_EVIDENCE_INDEX_<YYYYMMDD>_<short_commit_sha>.md

### Non-Release Boundary

Mini-EPIC 32.7 intentionally does not introduce:

- Docker packaging
- deployment
- staging environment
- production environment
- semantic version tag creation
- GitHub Release creation
- changelog generation
- artifact publishing
- rollback implementation
- environment promotion automation
- frontend UI changes
- runtime release registry
- database persistence for release evidence

### Relationship To Prior Mini-EPICs

Mini-EPIC 32.5 introduced bounded runtime release identity metadata.

Mini-EPIC 32.6 allowed CI validation jobs to inject safe release identity metadata.

Mini-EPIC 32.7 keeps validation evidence traceability separate from runtime identity and release publication.

This preserves a clean boundary:

    runtime release identity != validation evidence index != release publication

## Mini-EPIC 32.8 - Release Artifact Boundary and Package Manifest Design

Mini-EPIC 32.8 defines the future release artifact/package boundary for InvoMatch.

This is a documentation-first architecture step. It does not create a package, Docker image, deployment workflow, semantic version tag, GitHub Release, published artifact, changelog generator, rollback mechanism, environment promotion workflow, runtime release registry, or database-backed release evidence store.

The release package is defined as a bounded release candidate handoff unit tied to:

- a specific package identity
- a source commit SHA
- a branch/ref
- a related release candidate evidence index
- a validation status reference
- explicitly included components
- explicitly excluded components
- build environment assumptions
- reproducibility notes
- a non-deployment boundary

The package manifest is not the evidence index.

The package manifest identifies the package and its boundary.

The evidence index maps validation evidence and release candidate evidence references.

The architecture definition is documented in:

- `docs/architecture/RELEASE_ARTIFACT_PACKAGE_MANIFEST.md`

Mini-EPIC 32.8 intentionally keeps package generation out of scope. Future packaging work may implement manifest generation and validation only after this boundary is stable.

## Mini-EPIC 32.9 - Package Manifest Generator Dry-Run Contract

### Architecture Decision

Mini-EPIC 32.9 defines the package manifest dry-run boundary and introduces a minimal local-only generator script.

The dry-run generator exists only to produce a manifest preview. It is not a release package builder and does not publish, tag, deploy, promote, or persist release state.

### Dry-Run Generator Boundary

The generator may:
- read local git metadata
- reference documented package manifest expectations
- build a preview JSON structure
- print the preview to stdout
- optionally write the preview to output/local/release_manifest_dry_run/package_manifest_preview.json

The generator must mark every preview with:

{
  "dry_run": true,
  "package_status": "preview"
}

### Non-Release Boundary

The dry-run generator must not:
- create a package archive
- create a ZIP or tar file
- publish artifacts
- create Docker images
- create semantic version tags
- create GitHub Releases
- deploy anything
- modify CI
- write release state to a database
- promote environments
- generate changelogs
- implement rollback
- create a runtime release registry

### Validation Boundary

Because Mini-EPIC 32.9 introduces implementation, targeted tests are required.

The tests validate:
- dry-run status
- preview package status
- expected manifest field list
- non-deployment flags
- local-only default output path
- JSON preview writing to an explicitly requested local path

### Relationship To Mini-EPIC 32.8

Mini-EPIC 32.8 documented the release artifact/package boundary and package manifest design.

Mini-EPIC 32.9 does not create that package. It only defines and validates a safe preview contract for the future package manifest.

## Mini-EPIC 32.10 - Clean-State Package Manifest Dry-Run Evidence

Mini-EPIC 32.10 verifies the expected post-commit behavior of the package manifest dry-run generator after the Mini-EPIC 32.9 implementation has been committed and pushed.

The dry-run manifest generator remains a local-only evidence and preview tool. It does not create release packages, deployment artifacts, semantic version tags, GitHub Releases, Docker images, environment promotions, or published artifacts.

Clean-state verification rule:

- The dry-run manifest must continue to report `dry_run: true`.
- The package status must remain `preview`.
- The source identity branch must resolve to `main` when executed from the main branch.
- The source identity commit SHA must match repository `HEAD`.
- The source identity working-tree flag must report `working_tree_clean: true` when executed from a clean repository state.
- All non-deployment boundary flags must remain `false`.

Verified clean-state evidence from Mini-EPIC 32.10:

- `HEAD`: `e177e7fe4bcb9fe394dd2828f0098f5ddeef9dbf`
- `source_identity.commit_sha`: `e177e7fe4bcb9fe394dd2828f0098f5ddeef9dbf`
- `source_identity.branch`: `main`
- `source_identity.working_tree_clean`: `true`
- `dry_run`: `true`
- `package_status`: `preview`
- targeted validation: `5 passed in 0.12s`

This rule aligns dry-run evidence with repository state after commit/push and prevents the preview manifest from being misrepresented as a real release package or deployment artifact.

The clean-state verification is intentionally documented as evidence behavior rather than converted into a live repository cleanliness test. Repository cleanliness is an execution-state property and should not be hard-coded into deterministic tests unless isolated through a temporary git fixture.

## Mini-EPIC 32.11 - Release Package Manifest Deterministic Content Contract

Mini-EPIC 32.11 defines and validates the deterministic content contract for the future release package manifest preview.

This Mini-EPIC upgrades the dry-run output from a field-list preview into a structured content preview with required top-level sections.

The dry-run preview now declares:

- `package_identity`
- `source_identity`
- `evidence_reference`
- `included_components`
- `excluded_components`
- `build_environment_assumptions`
- `reproducibility_notes`
- `non_deployment_boundary`

### Content Contract Decision

The current dry-run generator should emit structured placeholder content for the required package manifest sections.

This is necessary because a field list alone does not validate the shape of the future package manifest.

The structured content remains deterministic and preview-only.

The dry-run generator must not invent:
- real package IDs
- real release candidate IDs
- creation timestamps
- semantic versions
- package archives
- deployment records
- release publication state

### Deterministic Preview Rules

The dry-run preview must keep these invariants:

- `dry_run: true`
- `package_status: preview`
- `package_identity.package_status: preview`
- `package_identity.package_type: dry-run-preview`
- all `non_deployment_boundary` flags are `false`
- evidence included in package is empty because no package exists
- validation execution timestamp is not invented
- local runtime databases are excluded
- local preview output is excluded
- dependency caches are excluded
- deployment artifacts are excluded
- GitHub Releases and semantic version tags are excluded

### Relationship To Future Packaging

Mini-EPIC 32.11 does not create a release package.

The future package manifest remains a separate release artifact concept defined in:

- `docs/architecture/RELEASE_ARTIFACT_PACKAGE_MANIFEST.md`

The dry-run preview remains a local JSON validation output. It is not the future package manifest artifact and must not be published as a release package.

### Validation

Targeted tests validate:

- required top-level section presence
- expected field model alignment
- deterministic placeholder stability
- JSON serializability
- dry-run and preview invariants
- non-deployment boundary invariants
- included/excluded component declaration
- local-only output path behavior

Mini-EPIC 32.11 remains contract/test-only and does not modify CI, create packages, publish artifacts, tag releases, create GitHub Releases, deploy, promote environments, or persist release state.

## Mini-EPIC 32.12 - Release Package Manifest Schema Validator

Mini-EPIC 32.12 adds a local schema validation layer for the release package manifest dry-run preview.

The validator is implemented inside the local dry-run generator boundary and validates the structured preview before it is printed or written to the local preview path.

### Schema Validation Decision

The dry-run manifest preview must now be rejected if required schema fields are missing, unsafe, or inconsistent with dry-run behavior.

The validator enforces:

- required top-level manifest sections
- required `package_identity` fields
- required `source_identity` fields
- required `evidence_reference` fields
- non-empty mappings for included and excluded component boundaries
- expected `non_deployment_boundary` keys
- all `non_deployment_boundary` values remaining `false`
- `dry_run: true`
- `package_status: preview`
- JSON serializability

The validator intentionally allows `evidence_reference.evidence_included_in_package` to be an empty list because the dry-run does not create or include package artifacts.

### Deterministic Failure Behavior

Schema failures use deterministic messages prefixed with:

~~~text
manifest schema invalid:
~~~

This keeps invalid preview failures testable and prevents silent drift in the manifest contract.

### Validation

Targeted tests cover:

- acceptance of the current deterministic preview
- missing top-level section rejection
- missing nested `package_identity` field rejection
- missing `source_identity` field rejection
- missing `evidence_reference` field rejection
- unsafe non-deployment boundary flag rejection
- wrong `dry_run` value rejection
- wrong `package_status` rejection
- non-JSON-serializable manifest rejection
- validated local preview writing

Mini-EPIC 32.12 remains local-only. It does not create packages, ZIP/tar archives, Docker images, semantic version tags, GitHub Releases, deployments, CI workflow changes, runtime release registry entries, database persistence, artifact publishing, rollback behavior, or environment promotion.

## Mini-EPIC 32.13 - Release Package Manifest Preview CLI Failure Contract

Mini-EPIC 32.13 defines and validates the command-line failure contract for the release package manifest dry-run generator.

### CLI Failure Boundary Decision

The dry-run generator now has a controlled CLI error boundary for known dry-run safety failures.

Schema validation still happens before stdout output and before optional local preview writing.

If validation fails, the CLI must:

- return a non-zero exit code
- write the deterministic validation error to stderr
- avoid printing partial manifest JSON to stdout
- avoid writing the requested preview output file
- remain local-only

This prevents invalid manifest previews from being mistaken for valid JSON output or local preview files.

### Implementation Boundary

The CLI execution path is separated into a small internal runner and a public `main()` boundary.

The runner performs argument parsing, manifest construction, schema validation, and success output.

The public `main()` catches `ReleaseManifestDryRunError`, writes the deterministic error to stderr, and returns exit code `1`.

This keeps known dry-run validation failures deterministic without converting unrelated programming errors into silent release behavior.

### Validation

Targeted tests cover:

- schema failure returns non-zero exit code
- schema failure writes deterministic stderr
- schema failure writes no stdout JSON
- schema failure writes no preview file
- valid stdout preview remains JSON
- valid preview keeps `dry_run: true`
- valid preview keeps `package_status: preview`
- valid `--write-preview` writes only the requested local preview file

Mini-EPIC 32.13 remains local-only. It does not create packages, ZIP/tar archives, Docker images, semantic version tags, GitHub Releases, deployments, CI workflow changes, runtime release registry entries, database persistence, artifact publishing, rollback behavior, frontend UI changes, or environment promotion.

## Mini-EPIC 32.14 - Release Package Manifest CLI Success Contract and Output Channel Discipline

Mini-EPIC 32.14 defines and validates the successful command-line output contract for the release package manifest dry-run generator.

Mini-EPIC 32.13 established the deterministic CLI failure contract. Mini-EPIC 32.14 completes the matching success-side contract so that both valid and invalid CLI outcomes are predictable.

### CLI Success Boundary Decision

The dry-run generator now has two explicit success modes:

- stdout JSON preview mode
- explicit --write-preview local file mode

When the CLI runs without --write-preview, stdout is reserved for valid manifest JSON only.

When the CLI runs with --write-preview, stdout is reserved for a deterministic human-readable success message only, and the manifest JSON is written only to the requested local output path.

stderr must remain silent for both success modes.

### stdout JSON Preview Mode

The default success mode must:

- return exit code 0
- emit valid manifest JSON to stdout
- emit nothing to stderr
- write no preview files
- preserve dry_run: true
- preserve package_status: preview

This keeps default CLI output machine-readable and safe for future automation.

### --write-preview Mode

The file-writing success mode must:

- return exit code 0
- write the preview only to the requested local output path
- emit no manifest JSON to stdout
- emit a deterministic human-readable success message to stdout
- emit nothing to stderr
- preserve dry_run: true
- preserve package_status: preview

A custom output path must not also create the default preview path.

### Test Coverage

Mini-EPIC 32.14 adds targeted tests for:

- stdout JSON success output
- stderr silence on success
- default mode avoiding preview file creation
- --write-preview writing only the requested local file
- --write-preview avoiding JSON emission to stdout
- deterministic success message output
- preservation of dry-run and preview status invariants

### Boundary

Mini-EPIC 32.14 remains local-only.

It does not create packages, ZIP/tar archives, Docker images, semantic version tags, GitHub Releases, deployments, CI workflow changes, runtime release registry entries, database persistence, artifact publishing, rollback behavior, frontend UI changes, or environment promotion.

## Mini-EPIC 32.15 - Release Manifest CLI Clean-State Success/Failure Evidence Verification

Status: Closed.

Mini-EPIC 32.15 verified the release package manifest dry-run CLI contract from a clean, pushed repository state using real command-line executions.

This was an evidence hardening step only. It did not introduce new product behavior, package generation, deployment behavior, manifest schema changes, CI workflow changes, frontend changes, runtime release registry behavior, database persistence, release tags, GitHub Releases, or artifact publishing.

### Confirmed Starting State

The repository was verified before evidence capture:

- Branch: main
- Branch status: up to date with origin/main
- Working tree: clean
- Latest commit: 8a94841 test: define release manifest dry-run cli success contract

Recent related commits:

- 8a94841 test: define release manifest dry-run cli success contract
- 25366b5 docs: finalize mini epic 32.13 clean-state evidence
- a8a0265 test: define release manifest dry-run cli failure contract

### Real CLI Evidence - stdout JSON Preview Mode

Command executed through the real CLI without --write-preview.

Evidence captured locally under:

    output/local/release_manifest_dry_run/mini_epic_32_15/

Captured files:

- stdout_json_mode.stdout.json
- stdout_json_mode.stderr.txt
- stdout_json_mode.exit_code.txt

Observed result:

- Exit code: 0
- stderr length: 0
- stdout parsed successfully as JSON
- dry_run: true
- package_status: preview
- default preview file was not written

This confirms that stdout JSON mode emits the manifest JSON to stdout, emits nothing to stderr, returns success, and does not write a preview file unless explicitly requested.

### Real CLI Evidence - Explicit --write-preview Mode

Command executed through the real CLI with:

- --write-preview
- explicit --output output\local\release_manifest_dry_run\mini_epic_32_15\requested_package_manifest_preview.json

Evidence captured locally under:

    output/local/release_manifest_dry_run/mini_epic_32_15/

Captured files:

- write_preview_mode.stdout.txt
- write_preview_mode.stderr.txt
- write_preview_mode.exit_code.txt
- requested_package_manifest_preview.json

Observed result:

- Exit code: 0
- stderr length: 0
- requested preview file exists
- default preview file was not written
- stdout contained deterministic human-readable success output
- stdout did not start with a JSON object
- stdout did not contain the dry_run manifest key
- written preview file parsed successfully as JSON
- written preview file contained dry_run: true
- written preview file contained package_status: preview

This confirms that explicit write-preview mode writes only the requested local preview file, emits a deterministic human-readable success message, emits no manifest JSON to stdout, and emits nothing to stderr.

### Targeted Validation

Command:

    pytest -q tests\test_release_manifest_dry_run.py --basetemp=.pytest_tmp

Result:

    23 passed in 0.36s

### Boundary Confirmation

Mini-EPIC 32.15 introduced no:

- real package creation
- ZIP or tar generation
- Docker packaging
- deployment
- staging or production promotion
- semantic version tags
- GitHub Release creation
- changelog generation
- artifact publishing
- rollback implementation
- runtime release registry
- database persistence
- CI workflow modification
- frontend UI changes
- manifest schema changes
- release identity semantic changes
- CLI output behavior changes
- package publishing behavior

The generated evidence remains local-only under output/local/ and is excluded from release package semantics.

## Mini-EPIC 32.16 - Release Manifest CLI Real Failure Evidence Verification

Mini-EPIC 32.16 verified the release package manifest dry-run CLI deterministic failure contract through real command-line execution.

The evidence confirmed that an invalid manifest schema condition:

- returns a non-zero exit code
- emits nothing to stdout
- emits deterministic validation output to stderr
- includes the expected validation prefix manifest schema invalid:
- does not write the requested preview file
- does not write the default preview file

The verified failure text was:

    manifest schema invalid: dry_run must be true

The evidence was captured through a local-only command-line execution that used the existing test-supported invalid manifest mechanism.

No public CLI flag, schema behavior, package behavior, release behavior, CI workflow, frontend behavior, or runtime behavior was changed.

Targeted validation after evidence capture:

    pytest -q tests\test_release_manifest_dry_run.py --basetemp=.pytest_tmp
    23 passed in 0.16s

Closure document:

    docs/architecture/MINI_EPIC_32_16_CLOSURE.md

## Mini-EPIC 32.17 - Release Manifest Evidence Index Final Alignment

Mini-EPIC 32.17 finalizes the release manifest dry-run evidence reference model.

The release candidate evidence index now provides a stable citation point for both dry-run CLI success-path evidence and deterministic failure-path evidence.

Future release-candidate records should cite:

- docs/architecture/RELEASE_CANDIDATE_EVIDENCE_INDEX.md as the primary evidence reference model
- docs/architecture/PACKAGE_MANIFEST_DRY_RUN_CONTRACT.md for the dry-run CLI and manifest-preview contract
- docs/architecture/MINI_EPIC_32_15_CLOSURE.md when concrete success-path evidence is needed
- docs/architecture/MINI_EPIC_32_16_CLOSURE.md when concrete failure-path evidence is needed

This alignment avoids copying full closure evidence into future release-candidate documentation while preserving traceability.

This Mini-EPIC does not change source code, tests, CLI semantics, manifest schema, CI workflow, packaging behavior, artifact publishing, deployment behavior, release identity semantics, frontend behavior, runtime registry behavior, database persistence, rollback behavior, tags, GitHub Releases, or environment promotion.

Dry-run previews remain local-only validation evidence and are not release artifacts.

## Mini-EPIC 32.18 - Release Candidate Dry-Run Evidence Record Template

Mini-EPIC 32.18 defines a reusable release-candidate evidence record template:

- `docs/architecture/RELEASE_CANDIDATE_EVIDENCE_RECORD_TEMPLATE.md`

Future release-candidate validation runs should copy this template to create a concrete evidence record and then fill it with actual observed command results.

The template standardizes evidence capture across:

- source identity
- branch and commit state
- repository cleanliness
- local validation command evidence
- CI validation evidence, when available
- release identity metadata checks
- release manifest dry-run stdout JSON mode
- release manifest dry-run write-preview mode
- release manifest dry-run failure-path references
- generated output tracking checks
- non-deployment boundary confirmation
- reviewer/signoff notes

This template is documentation structure only. It does not create a release candidate, generate a package, publish artifacts, change CLI behavior, add release automation, replace validation execution, or claim release readiness without observed evidence.

The full template is intentionally not duplicated in this EPIC document. The canonical scaffold lives in `RELEASE_CANDIDATE_EVIDENCE_RECORD_TEMPLATE.md`.

## Mini-EPIC 32.19 — Release Candidate Evidence Record Dry-Run Instance

Mini-EPIC 32.19 created the first concrete release-candidate evidence record instance from the reusable template introduced in Mini-EPIC 32.18.

Created record:

docs/architecture/RELEASE_CANDIDATE_EVIDENCE_RECORD_LOCAL_DRY_RUN_001.md

This Mini-EPIC remains evidence capture only. It does not create a real release candidate, package, artifact, deployment, tag, GitHub Release, CI change, or production-readiness claim.
