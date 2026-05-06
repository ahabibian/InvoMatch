# Mini-EPIC 32.11 Closure - Release Package Manifest Deterministic Content Contract

## Status

Closed pending commit and push.

## Context

Mini-EPIC 32.10 verified clean-state behavior for the local-only package manifest dry-run generator.

Mini-EPIC 32.11 extends that foundation by defining and validating a deterministic structured content contract for the dry-run manifest preview.

The previous dry-run output listed expected future manifest fields, but it did not emit structured placeholder sections for those fields.

That was insufficient for a future package manifest contract because a field list alone does not validate section shape, deterministic placeholder semantics, or included/excluded component boundaries.

## Objective

Define and validate the deterministic content contract for the future release package manifest preview without creating a real release package.

## Content Contract Decision

The dry-run generator now emits structured placeholder content for the required future package manifest sections.

Required top-level content sections are:

- `package_identity`
- `source_identity`
- `evidence_reference`
- `included_components`
- `excluded_components`
- `build_environment_assumptions`
- `reproducibility_notes`
- `non_deployment_boundary`

The dry-run preview remains JSON and local-only.

The future real package manifest remains a separate package artifact concept defined in:

- `docs/architecture/RELEASE_ARTIFACT_PACKAGE_MANIFEST.md`

Mini-EPIC 32.11 does not create that real package manifest artifact.

## Implementation Summary

### Dry-Run Generator

Updated:

- `scripts/release_manifest_dry_run.py`

The generator now emits deterministic preview sections for:

- package identity
- evidence references
- included components
- excluded components
- build environment assumptions
- reproducibility notes

The generator continues to emit:

- `schema_version`
- `dry_run`
- `package_status`
- `source_identity`
- `documentation_references`
- `expected_manifest_fields`
- `non_deployment_boundary`

### Deterministic Preview Placeholders

The preview deliberately avoids volatile or false release claims.

Examples:

- `package_id`: `preview-not-created`
- `package_created_at`: `not-created-in-dry-run`
- `release_candidate_id`: `preview-only`
- `release_version`: `not-assigned-in-dry-run`
- `validation_status`: `not-executed-by-dry-run`
- `validation_executed_at`: `not-executed-by-dry-run`
- generated artifact reproducibility: `not-applicable-in-dry-run`

These placeholders are intentional.

They prevent the dry-run from pretending that a package, timestamp, validation run, semantic version, release candidate, or artifact has been created.

### Included Component Preview

The preview declares future package boundary areas as preview-only:

- backend source
- backend tests
- frontend source
- architecture documentation
- release evidence index
- package manifest contract

These are not copied into any package by this Mini-EPIC.

### Excluded Component Preview

The preview explicitly excludes:

- local runtime databases
- local preview outputs
- dependency caches
- deployment artifacts
- public release objects

Examples include:

- `output/local/reconciliation_runs.sqlite3`
- `output/local/review_store.sqlite3`
- `output/local/exports/export_artifacts.sqlite3`
- `output/local/release_manifest_dry_run/package_manifest_preview.json`
- `.venv/`
- `node_modules/`
- `.pytest_tmp/`
- Docker images
- deployment credentials
- GitHub Releases
- semantic version tags

## Documentation Updated

Updated:

- `docs/architecture/PACKAGE_MANIFEST_DRY_RUN_CONTRACT.md`
- `docs/architecture/EPIC_32_RELEASE_PIPELINE.md`

The documentation now distinguishes:

1. Dry-run manifest preview
2. Future package manifest
3. Real package artifact

The documentation states that the dry-run preview is local JSON validation output and must not be treated as a release package, release artifact, published artifact, GitHub Release, deployment, promotion, or runtime release registry entry.

## Tests Updated

Updated:

- `tests/test_release_manifest_dry_run.py`

Targeted tests now validate:

- dry-run status remains true
- package status remains preview
- package identity remains preview-only
- required top-level content sections exist
- expected field list matches the required section model
- deterministic placeholders are stable
- all non-deployment boundary flags remain false
- included and excluded components are declared
- output remains JSON-serializable
- default output path remains local and non-release
- optional preview writing remains explicitly local and preview-only

## Validation Evidence

### Baseline Before Mini-EPIC 32.11 Changes

Command:

~~~powershell
cd C:\dev\InvoMatch
$env:PYTHONPATH = "src"
pytest -q tests\test_release_manifest_dry_run.py --basetemp=.pytest_tmp
~~~

Result:

~~~text
5 passed in 0.14s
~~~

### Targeted Validation After Generator and Test Update

Command:

~~~powershell
cd C:\dev\InvoMatch
$env:PYTHONPATH = "src"
pytest -q tests\test_release_manifest_dry_run.py --basetemp=.pytest_tmp
~~~

Result:

~~~text
9 passed in 0.13s
~~~

### Targeted Validation After Documentation Update

Command:

~~~powershell
cd C:\dev\InvoMatch
$env:PYTHONPATH = "src"
pytest -q tests\test_release_manifest_dry_run.py --basetemp=.pytest_tmp
~~~

Result:

~~~text
9 passed in 0.25s
~~~

### Dry-Run Preview Stdout Check

Command:

~~~powershell
cd C:\dev\InvoMatch
python scripts\release_manifest_dry_run.py
~~~

Observed invariant values:

- `dry_run`: `true`
- `package_status`: `preview`
- `package_identity.package_status`: `preview`
- `package_identity.package_type`: `dry-run-preview`
- `evidence_reference.validation_status`: `not-executed-by-dry-run`
- all `non_deployment_boundary` flags remained `false`

During this check, `source_identity.working_tree_clean` was `false` because Mini-EPIC 32.11 files were modified locally before commit.

That is expected during active implementation and is not used as clean-state evidence.

Clean-state dry-run behavior must be verified only after commit and push.

## Files Changed

- `scripts/release_manifest_dry_run.py`
- `tests/test_release_manifest_dry_run.py`
- `docs/architecture/PACKAGE_MANIFEST_DRY_RUN_CONTRACT.md`
- `docs/architecture/EPIC_32_RELEASE_PIPELINE.md`
- `docs/architecture/MINI_EPIC_32_11_CLOSURE.md`

## Boundary Confirmation

Mini-EPIC 32.11 did not create:

- real package archive
- ZIP archive
- tar archive
- Docker image
- deployment
- staging environment
- production environment
- semantic version tag
- GitHub Release
- changelog generator
- artifact publishing flow
- rollback implementation
- environment promotion automation
- frontend UI changes
- runtime release registry
- database persistence for release evidence
- CI workflow changes
- published dry-run preview artifact

The dry-run preview remains a local-only contract validation output.

## Exit Criteria Review

| Exit Criteria | Status |
|---|---|
| Deterministic manifest content contract documented | Met |
| Dry-run output has required section model | Met |
| Targeted tests validate required section model | Met |
| `dry_run` remains true | Met |
| `package_status` remains preview | Met |
| Non-deployment boundary flags remain false | Met |
| No real package/deployment/tag/release created | Met |
| EPIC 32 documentation updated | Met |
| Mini-EPIC 32.11 closure document created | Met |
| Added/updated tests pass | Met |
| Working tree clean | Pending final commit/push verification |
| Changes committed and pushed | Pending |

## Closure Assessment

Mini-EPIC 32.11 successfully defines and validates the deterministic content contract for the release package manifest dry-run preview.

The project now has a stricter preview contract for future release packaging without crossing into package generation, artifact publishing, deployment, release tagging, or CI workflow modification.