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