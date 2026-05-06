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