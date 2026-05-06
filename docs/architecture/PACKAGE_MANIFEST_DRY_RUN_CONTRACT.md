# Package Manifest Dry-Run Contract

## Status

Updated for Mini-EPIC 32.11.

This document defines the safe dry-run boundary for generating an InvoMatch release package manifest preview.

Mini-EPIC 32.11 upgrades the previous field-list preview into a deterministic structured content contract.

## Purpose

The package manifest dry-run exists to preview the metadata shape of a future release artifact package without creating, publishing, tagging, deploying, or registering any release artifact.

It is a local validation and preview mechanism only.

The dry-run manifest preview is not a package, not a release candidate artifact, not a deployment record, and not a release registry entry.

## Architecture Decision

Mini-EPIC 32.9 introduced a local-only dry-run manifest generator.

Mini-EPIC 32.10 verified clean-state dry-run behavior after commit/push.

Mini-EPIC 32.11 defines the deterministic content contract for the preview output.

The dry-run generator may:
- read repository metadata
- reference documented release manifest expectations
- produce a manifest preview
- print the preview to stdout
- optionally write the preview to a clearly local non-release output path

The dry-run generator must not:
- create a package archive
- create a ZIP file
- create a tar file
- publish artifacts
- create Docker images
- create semantic version tags
- create GitHub Releases
- deploy anything
- modify CI workflows
- write release state to a database
- promote environments
- generate a changelog
- create rollback automation
- create runtime release registry entries

## Dry-Run Output Boundary

Any generated output must be marked as dry-run and preview-only.

Required invariant fields:

~~~json
{
  "dry_run": true,
  "package_status": "preview"
}
~~~

The output is not a release artifact and must not be interpreted as a release candidate package.

## Local Output Path Boundary

The default local preview path is:

~~~text
output/local/release_manifest_dry_run/package_manifest_preview.json
~~~

This path is intentionally under `output/local` and is not a release artifact publishing location.

The file may be deleted at any time.

## Required Top-Level Preview Sections

The dry-run preview must include these structured top-level sections:

- `package_identity`
- `source_identity`
- `evidence_reference`
- `included_components`
- `excluded_components`
- `build_environment_assumptions`
- `reproducibility_notes`
- `non_deployment_boundary`

The preview may also include support sections such as:

- `schema_version`
- `dry_run`
- `package_status`
- `documentation_references`
- `expected_manifest_fields`

## Package Identity Preview

The dry-run preview must include a deterministic package identity placeholder.

It must not invent a real package ID, release candidate ID, timestamp, semantic version, or release channel.

Required dry-run behavior:
- `package_status` remains `preview`
- `package_type` remains `dry-run-preview`
- `package_id` clearly indicates that no package was created
- `package_created_at` clearly indicates that no creation timestamp exists in dry-run mode
- release identity remains preview-only

## Source Identity

The generator reads source identity from the local git checkout.

Required source identity fields:

- `branch`
- `commit_sha`
- `working_tree_clean`

If git metadata cannot be read, the generator must fail rather than invent release identity.

`working_tree_clean` is an execution-state field. It may be false while the current Mini-EPIC is being edited and true after commit/push verification.

## Evidence Reference Preview

The dry-run preview must reference the evidence index contract without claiming that validation was executed by the dry-run itself.

Required dry-run behavior:
- evidence index path is declared
- evidence index version is declared
- validation status is explicit
- validation execution timestamp is not invented
- evidence included in package remains empty because no package exists
- evidence referenced only may point to the evidence index

## Included Components Preview

The dry-run preview must declare the future package boundary areas as preview-only inclusions.

Allowed preview inclusions include:
- backend source
- backend tests
- frontend source
- architecture documentation
- release evidence index
- package manifest contract

Each included component must remain descriptive. It must not imply that files were copied into a package.

## Excluded Components Preview

The dry-run preview must explicitly exclude non-package and non-release materials.

Required exclusion groups include:
- local runtime databases
- local preview outputs
- dependency caches
- deployment artifacts
- public release objects

Examples:
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

## Build Environment Assumptions Preview

The dry-run preview must document assumptions needed to reproduce or inspect future package generation.

The preview may use deterministic placeholders instead of probing machine-specific tool versions.

Required areas:
- operating system family
- shell
- Python runtime assumption
- Node runtime assumption
- npm runtime assumption
- package manager assumptions
- required environment variables
- external service assumptions
- database assumptions

The preview must not convert local runtime state into package metadata.

## Reproducibility Notes Preview

The dry-run preview must explain what can and cannot be reproduced.

Required areas:
- reproducible from commit
- validation reproducibility
- generated artifact reproducibility
- local machine dependency notes
- known non-reproducible items

Dry-run output must avoid volatile timestamps and local absolute paths inside deterministic contract fields.

## Documentation References

The dry-run preview references the release documentation that defines the current package boundary:

- `docs/architecture/EPIC_32_RELEASE_PIPELINE.md`
- `docs/architecture/RELEASE_ARTIFACT_PACKAGE_MANIFEST.md`
- `docs/architecture/RELEASE_CANDIDATE_EVIDENCE_INDEX.md`
- `docs/architecture/PACKAGE_MANIFEST_DRY_RUN_CONTRACT.md`

The generator does not parse these documents as a release registry. They remain human-governed architecture documents.

## Expected Manifest Fields

The preview must list the expected future package manifest areas:

- `package_identity`
- `source_identity`
- `evidence_reference`
- `included_components`
- `excluded_components`
- `build_environment_assumptions`
- `reproducibility_notes`
- `non_deployment_boundary`

The listed expected fields must match the structured top-level content sections present in the dry-run preview.

## Non-Deployment Boundary Flags

The dry-run preview must explicitly include all of these as false:

- `creates_package_archive`
- `publishes_artifacts`
- `creates_docker_image`
- `creates_git_tag`
- `creates_github_release`
- `deploys`
- `modifies_ci`
- `writes_release_state_to_database`
- `promotes_environment`

## Validation Expectations

The dry-run generator must have targeted tests.

Tests must verify:
- dry-run status is true
- package status is preview
- required top-level sections exist
- expected field list matches the section model
- deterministic placeholder fields are stable
- non-deployment flags are false
- included and excluded components are declared
- output remains JSON-serializable
- default output path is local and non-release
- JSON preview writing only writes to an explicitly requested local path
- no packaging or deployment behavior is represented as enabled

## Relationship To Future Package Manifest

The future package manifest may become a YAML file named:

~~~text
release-package-manifest.yaml
~~~

The dry-run preview remains JSON because it is a local validation output and easy to test deterministically.

The dry-run preview is not the future canonical package manifest. It is a contract preview for the future manifest.

## Current Boundary

Mini-EPIC 32.11 introduces only:
- a deterministic structured dry-run content contract
- expanded local-only preview fields
- targeted tests for the section model
- documentation alignment
- closure evidence

It does not introduce real release packaging.