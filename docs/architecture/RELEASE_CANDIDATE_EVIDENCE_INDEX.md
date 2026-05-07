# Release Candidate Evidence Index

## Status

Defined.

This document defines the release candidate evidence index / manifest boundary for InvoMatch release candidate validation runs.

It is documentation-first and does not create a package, deployment, tag, GitHub Release, public artifact, promotion event, rollback record, or runtime release registry.

## Purpose

A release candidate validation run may produce multiple pieces of evidence:

- backend test results
- operational validation results
- contract/API validation results
- scenario regression results
- frontend lint results
- frontend build results
- closure documents
- release pipeline notes
- CI validation metadata, when available

The evidence index exists to record which evidence belongs to one validation run.

It is not a release declaration.

It is not a promotion record.

It is not a deployment record.

It is not runtime truth.

## Boundary

The evidence index is a documentation artifact.

It may reference:

- commit SHA
- branch/ref
- validation date/time as documented evidence
- validation source
- validation command groups
- result summaries
- related closure documents
- related evidence files or logs

The evidence index must not:

- create or imply a semantic version tag
- create or imply a GitHub Release
- create a package
- publish artifacts
- deploy to staging or production
- promote a build
- define rollback behavior
- store runtime release state
- persist release evidence in a database
- replace CI logs or local command outputs
- claim production readiness by itself

## Evidence Source Classification

Each indexed validation group must identify its source.

Allowed values:

| Source | Meaning |
|---|---|
| `local` | Evidence was produced by a local developer/operator validation command. |
| `ci` | Evidence was produced by a CI validation workflow. |
| `mixed` | Evidence combines local and CI validation references. |
| `documented` | Evidence is documented as a format/example/closure note, not produced by a live validation run. |

## Recommended File Location

Release candidate evidence index files should be stored under:

    docs/architecture/evidence/release_candidates/

Recommended naming pattern:

    RC_EVIDENCE_INDEX_<YYYYMMDD>_<short_commit_sha>.md

Example:

    docs/architecture/evidence/release_candidates/RC_EVIDENCE_INDEX_20260506_57d8d90.md

The naming pattern is descriptive only. It does not create a release tag or version.

## Evidence Index Format

Each evidence index should follow this structure.

    # Release Candidate Evidence Index - <short_commit_sha>

    ## Status

    Recorded.

    ## Non-Release Boundary

    This evidence index does not create a package, deployment, semantic version tag, GitHub Release, promotion, rollback point, changelog, or public artifact.

    ## Candidate Context

    | Field | Value |
    |---|---|
    | Commit SHA | <full_commit_sha> |
    | Short Commit SHA | <short_commit_sha> |
    | Branch / Ref | <branch_or_ref> |
    | Validation Date/Time | <documented_date_time> |
    | Validation Source | local / ci / mixed / documented |
    | Validation Status Claim | not_declared / passed / failed / partial |

    ## Important Interpretation

    The validation date/time is documented evidence only.

    It is not runtime release identity.

    It is not a build timestamp unless explicitly produced by a build process.

    The validation status claim describes the evidence index only and must not be treated as a production release readiness claim.

    ## Validation Command Groups

    | Group | Source | Command / Evidence Reference | Result Summary |
    |---|---|---|---|
    | Backend full validation | local | pytest ... | 699 passed |
    | Operational validation | local | pytest ... | 85 passed |
    | Contract/API validation | local | pytest ... | 47 passed |
    | Scenario regression pack | local | pytest ... | 4 passed |
    | Frontend lint | local | npm run lint | passed |
    | Frontend build | local | npm run build | passed |

    ## Related Closure Documents

    | Document | Purpose |
    |---|---|
    | docs/architecture/MINI_EPIC_32_X_CLOSURE.md | Closure evidence for the relevant Mini-EPIC. |

    ## Related Evidence Files

    | File | Source | Description |
    |---|---|---|
    | <path> | local / ci | <description> |

    ## Exclusions

    This index does not include:

    - release package
    - Docker image
    - deployment target
    - environment promotion
    - semantic version tag
    - GitHub Release
    - changelog
    - rollback implementation
    - runtime registry entry
    - database persistence

## Minimal Required Fields

A valid release candidate evidence index must include:

1. commit SHA
2. branch/ref
3. documented validation date/time
4. validation source
5. validation command groups
6. result summaries
7. related closure documents
8. non-release boundary statement

## Relationship To Release Identity

Mini-EPIC 32.5 introduced runtime release identity foundations.

Mini-EPIC 32.6 aligned CI validation with bounded release identity metadata.

This evidence index is separate from runtime release identity.

Runtime release identity may expose bounded metadata to operators.

The evidence index records validation evidence for engineering traceability.

Neither mechanism creates a release by itself.

## Future Extension Points

Future EPICs may introduce:

- generated evidence indexes from CI
- signed validation evidence
- release package manifests
- changelog generation
- semantic version tagging
- GitHub Release creation
- staging promotion records
- rollback metadata

Those are intentionally outside this boundary.

## Release Manifest Dry-Run Evidence Reference Model

The release manifest dry-run evidence is a release-candidate documentation reference model only.

It exists to make future release-candidate documentation cite a stable evidence structure instead of relying on scattered Mini-EPIC closure notes.

### Evidence Sources

| Evidence Area | Source | Purpose |
|---|---|---|
| Success-path dry-run CLI evidence | docs/architecture/MINI_EPIC_32_15_CLOSURE.md | Confirms clean-state dry-run CLI success evidence and successful preview behavior. |
| Failure-path dry-run CLI evidence | docs/architecture/MINI_EPIC_32_16_CLOSURE.md | Confirms deterministic CLI validation failure behavior from a clean pushed state. |
| Dry-run contract | docs/architecture/PACKAGE_MANIFEST_DRY_RUN_CONTRACT.md | Defines the expected dry-run CLI and manifest-preview contract. |
| Artifact boundary | docs/architecture/RELEASE_ARTIFACT_PACKAGE_MANIFEST.md | Defines the boundary between release artifact design and local dry-run preview behavior. |

### Success-Path Evidence Meaning

The success-path evidence from Mini-EPIC 32.15 confirms that the release manifest dry-run CLI can produce valid local preview evidence from a clean repository state.

This evidence may be cited by future release-candidate documentation when showing that the manifest dry-run command can complete successfully under the documented contract.

The success evidence does not imply:
- a real package was created
- a release artifact was published
- a deployment happened
- a GitHub Release was created
- a tag was created
- a release candidate was promoted

### Failure-Path Evidence Meaning

The failure-path evidence from Mini-EPIC 32.16 confirms that the release manifest dry-run CLI rejects invalid manifest preview content deterministically.

The verified failure behavior includes:
- non-zero exit code
- empty stdout
- deterministic stderr output
- expected validation prefix: manifest schema invalid:
- no requested preview file written
- no default preview file written

This failure evidence is validation behavior evidence only.

It is not a product feature, not a release feature, and not a deployment capability.

### Local-Only Evidence Boundary

Release manifest dry-run preview output is local-only evidence.

Dry-run preview files are not package artifacts.

Local preview output must not be treated as:
- a release artifact
- a package
- a deployment bundle
- a production artifact
- a staging artifact
- a published build
- a GitHub Release asset

Local generated evidence output must not be tracked unless a future Mini-EPIC explicitly changes the evidence storage policy.

### Future Release-Candidate Citation Rule

Future release-candidate documentation should cite this evidence model first, then cite the specific Mini-EPIC closure evidence only when the release-candidate record needs concrete historical verification.

Recommended citation order:

1. docs/architecture/RELEASE_CANDIDATE_EVIDENCE_INDEX.md
2. docs/architecture/PACKAGE_MANIFEST_DRY_RUN_CONTRACT.md
3. docs/architecture/MINI_EPIC_32_15_CLOSURE.md for success-path evidence
4. docs/architecture/MINI_EPIC_32_16_CLOSURE.md for failure-path evidence

This avoids duplicating full closure content in future release-candidate records while preserving traceability.

### Non-Deployment Boundary

Release manifest dry-run evidence capture does not imply release publishing.

It does not introduce:
- package generation
- artifact publishing
- Docker image creation
- ZIP or tar creation
- semantic version tagging
- GitHub Release creation
- deployment
- staging promotion
- production promotion
- runtime release registry updates
- database release-state persistence
- rollback behavior
- frontend behavior
- CI workflow behavior

## Release Candidate Evidence Record Template

Mini-EPIC 32.18 adds a reusable release-candidate evidence record template:

- `docs/architecture/RELEASE_CANDIDATE_EVIDENCE_RECORD_TEMPLATE.md`

The template is a documentation scaffold only.

It exists to make future release-candidate validation evidence consistent, reviewable, and copyable.

The template does not create a release candidate, does not create a release package, does not publish artifacts, does not replace validation execution, and does not declare release readiness by itself.

Each future release-candidate evidence record must contain actual observed command results from the validation activity being recorded. Expected results, copied prior outputs, or placeholder values are not valid evidence.

The template separates the following evidence areas:

- source identity
- branch and commit state
- repository cleanliness
- validation command evidence
- release manifest dry-run evidence
- success-path references
- failure-path references
- local-only evidence boundaries
- non-deployment boundary
- final reviewer/signoff notes

Release manifest dry-run evidence captured through this template remains local-only evidence unless a future release process explicitly promotes a generated output into a defined release artifact. Filling the template must not be treated as package generation or artifact publication.

## Local Dry-Run Evidence Record Instances

### RC-EVIDENCE-LOCAL-DRY-RUN-001

Document:

docs/architecture/RELEASE_CANDIDATE_EVIDENCE_RECORD_LOCAL_DRY_RUN_001.md

Type:

Local dry-run evidence record.

Boundary:

This record is not a release artifact, not a release package, not a deployment record, and not a production-readiness claim.

## Governing Policy Reference

Release candidate evidence record status must follow the finalization rules defined in:

- `docs/architecture/RELEASE_CANDIDATE_EVIDENCE_RECORD_FINALIZATION_GATE.md`

The evidence index remains a traceability index. It must not duplicate the full finalization process.rnMini-EPIC 32.22 Evidence Record Finalization Gate Application
Mini-EPIC 32.22 applied the Mini-EPIC 32.21 evidence record finalization gate to the first concrete local dry-run evidence record.
Reviewed record:


docs/architecture/RELEASE_CANDIDATE_EVIDENCE_RECORD_LOCAL_DRY_RUN_001.md


Classification result:


finalized-local-dry-run


This classification is evidence-status alignment only.
It does not create a release candidate, generate a package, publish artifacts, introduce release automation, deploy, modify CLI behavior, modify manifest schema, modify runtime behavior, or claim production readiness.
Closure record:


docs/architecture/MINI_EPIC_32_22_CLOSURE.md

rn

## First Finalized Local Dry-Run Baseline Reference

Mini-EPIC 32.23 establishes docs/architecture/RELEASE_CANDIDATE_EVIDENCE_RECORD_LOCAL_DRY_RUN_001.md as the first finalized local dry-run evidence baseline reference.

This baseline reference is internal evidence traceability only.

It records that the first concrete local dry-run evidence record was reviewed under the Mini-EPIC 32.21 finalization gate and classified in Mini-EPIC 32.22 as finalized-local-dry-run.

This reference does not create a release candidate, generate a package, publish artifacts, introduce release automation, deploy anything, modify CLI behavior, modify manifest schema, modify runtime code, change validation behavior, or claim production readiness.rn
Baseline Consumption Rules

The finalized local dry-run evidence baseline established by Mini-EPIC 32.23 may be referenced by future evidence records, audits, and dry-run validations only as an internal traceability reference.

Allowed uses:

comparison against later evidence records
audit continuity across release-candidate evidence work
consistency checks for future local dry-run evidence documentation
historical reference to the first finalized local dry-run evidence baseline

Disallowed interpretations:

it is not a release candidate
it is not a package artifact
it is not a deployment artifact
it is not an approval gate result
it is not a production-readiness signal
it does not replace future validation evidence
it does not prove that a future release candidate is ready

Any future evidence record that references this baseline must preserve the non-release, non-package, non-deployment, non-approval, and non-production-readiness boundary.

The baseline is useful for internal evidence traceability only. It must not be used as a substitute for fresh release-candidate validation, CI evidence, package evidence, deployment verification, or operational readiness evidence.rn

## Release Candidate Evidence Workflow Readiness Checklist

Status: documented pre-flight checklist for future release-candidate evidence workflow execution.

This checklist prepares future release-candidate evidence work only.

It does not create a release candidate, generate a package, publish artifacts, introduce release automation, deploy anything, create a new evidence record instance, or claim release-candidate or production readiness.

Before any future release-candidate evidence record is created or validated, the following must be confirmed:

- Mini-EPIC 32.23 closure exists and identifies the finalized local dry-run evidence baseline as a reference point only.
- Mini-EPIC 32.24 closure exists and defines how the finalized baseline may be consumed by future evidence work.
- The evidence index records that the finalized baseline cannot substitute for fresh validation evidence.
- EPIC 32 documentation records the finalized baseline and its non-release, non-package, non-deployment boundary.
- Future evidence records must identify their own execution context, including branch, commit, working tree state, validation commands, validation results, and evidence date.
- Required validation layers remain future execution requirements and are not satisfied by the baseline reference alone.
- Baseline references must follow the Mini-EPIC 32.24 consumption rules.
- Any future release-candidate evidence record must clearly distinguish reference baseline material from newly executed validation evidence.

Checklist outcome:

- If any prerequisite is missing, future release-candidate evidence execution must not proceed.
- If all prerequisites are present, future work may proceed to define or execute a real release-candidate evidence workflow in a later Mini-EPIC.

Boundary:

Passing this checklist does not mean the system is release-candidate ready, packaged, deployed, automated, or production ready.rn
Release Candidate Evidence Execution Record Template

Status: Template only.

This section defines the expected structure for future release-candidate evidence execution records.

It is based on the readiness checklist established in Mini-EPIC 32.25.

This template does not create a release candidate, does not create a real evidence execution record instance, does not execute validation, does not generate a package, does not publish artifacts, does not introduce automation, does not deploy anything, and does not claim release-candidate or production readiness.

Purpose

Future release-candidate evidence records must be repeatable, auditable, and clearly separated from baseline reference material.

Each future evidence record must distinguish between:

baseline references inherited from prior dry-run or checklist work
freshly executed validation evidence captured for the specific future release-candidate attempt

Baseline references may support traceability, but they must not be represented as newly executed evidence.

Required Record Metadata

Each future release-candidate evidence execution record must include:

record identifier
record title
record status
record creation date and time
record owner or executor
Mini-EPIC or release-candidate context
repository name
branch name
source commit SHA
working tree state at execution time
CI run identifier, if CI validation is part of the future execution
evidence index reference
readiness checklist reference
final evidence status

The record identifier must be stable enough to support audit references from later documents.

Required Source Identity Fields

Each future record must capture source identity as freshly observed execution context.

Required source identity fields:

branch
commit SHA
working tree clean status
repository remote, when relevant
timestamp of source identity capture
validation environment name or local execution context
runtime or toolchain versions, when relevant to the validation being executed

A future record must not rely only on older baseline documents for source identity.

Required Baseline-Reference Fields

Each future record must include a baseline-reference section.

Required baseline-reference fields:

referenced baseline document or checklist
referenced baseline date
referenced baseline commit, if available
purpose of the baseline reference
explicit statement that the baseline reference is not newly executed evidence
explanation of how the baseline informs the current future execution

Baseline references must be treated as historical traceability material unless the future record explicitly captures a fresh validation run.

Required Validation-Layer Result Sections

Each future release-candidate evidence execution record must include a result section for every required validation layer.

Required validation-layer sections:

Required Scenario Regression Pack
Operational Validation Pack
Contract Validation Pack
Full Backend Validation Pack
Frontend Lint
Frontend Build
Release identity and source traceability verification
Package manifest or package preview verification, if applicable to the future release-candidate stage
Evidence completeness review

Each validation-layer section must capture:

validation command or CI job name
execution location
execution timestamp or CI run timestamp
result status
observed output summary
failure output reference, if failed
repair commit reference, if repaired
re-validation evidence, if repaired
blocking status

A validation layer that was not executed must be marked as not executed and must not be treated as passed.

Required Failure and Blocker Section

Each future record must include a failure and blocker section.

The section must capture:

failed validation layer
failure summary
observed failure output reference
whether the failure blocks release-candidate evidence closure
owner of the repair action, if known
repair commit or change reference, if available
re-run evidence after repair
final blocker status

Any failed required validation layer must block release-candidate evidence closure until repaired and re-validated.

Required Non-Release Boundary Section

Each future record must include a non-release boundary section unless the project intentionally moves into a real release execution process through a separately approved Mini-EPIC.

For this current EPIC 32 documentation stage, the required boundary language is:

no release candidate was created
no package was generated
no public artifact was published
no deployment was performed
no release automation was introduced
no runtime behavior was changed
no CI behavior was changed by the evidence record itself
no production-readiness claim was made

If a future Mini-EPIC intentionally changes this boundary, that change must be documented separately before the evidence record claims any stronger release status.

Required Final Evidence Status Language

Each future record must end with a final evidence status section.

Allowed status language for future records:

Evidence template only
Evidence capture in progress
Evidence blocked
Evidence complete but not release-candidate ready
Evidence complete and ready for separate release-candidate decision review

The final evidence status must not imply production readiness unless production readiness is explicitly validated and approved in a separate release process.

Minimum Future Record Skeleton

A future release-candidate evidence execution record should use this minimum structure:

Record metadata
Source identity
Execution context
Baseline references
Required validation-layer results
Failure and blocker review
Evidence completeness review
Non-release or release-boundary statement
Final evidence status

This skeleton is mandatory for consistency, but future records may add more detailed subsections when needed.

Mini-EPIC 32.26 Outcome

Mini-EPIC 32.26 defines this reusable template only.

No real release-candidate evidence execution record instance is created by this Mini-EPIC.

No validation pack is executed by this Mini-EPIC.

No release candidate, package, deployment, automation, or production-readiness claim is introduced.rn