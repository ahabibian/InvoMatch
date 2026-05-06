# Package Manifest Dry-Run Contract

## Status

Defined for Mini-EPIC 32.9.

This document defines the safe dry-run boundary for generating an InvoMatch release package manifest preview.

## Purpose

The package manifest dry-run exists to preview the metadata shape of a future release artifact package without creating, publishing, tagging, deploying, or registering any release artifact.

It is a local validation and preview mechanism only.

## Architecture Decision

Mini-EPIC 32.9 introduces a dry-run manifest generator contract and a minimal local-only script.

This is intentionally not a packaging system.

The dry-run generator may:
- read repository metadata
- read documented release manifest expectations
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

Required fields:

{
  "dry_run": true,
  "package_status": "preview"
}

The output is not a release artifact and must not be interpreted as a release candidate package.

## Local Output Path Boundary

The default local preview path is:

output/local/release_manifest_dry_run/package_manifest_preview.json

This path is intentionally under output/local and is not a release artifact publishing location.

The file may be deleted at any time.

## Manifest Preview Required Fields

The dry-run preview must include:

- schema_version
- dry_run
- package_status
- source_identity
- documentation_references
- expected_manifest_fields
- non_deployment_boundary

## Source Identity

The generator reads source identity from the local git checkout.

Required source identity fields:

- branch
- commit_sha
- working_tree_clean

If git metadata cannot be read, the generator must fail rather than invent release identity.

## Documentation References

The dry-run preview references the release documentation that defines the current package boundary:

- docs/architecture/EPIC_32_RELEASE_PIPELINE.md
- docs/architecture/RELEASE_ARTIFACT_PACKAGE_MANIFEST.md
- docs/architecture/RELEASE_CANDIDATE_EVIDENCE_INDEX.md

The generator does not parse these documents as a release registry. They remain human-governed architecture documents.

## Expected Manifest Fields

The preview must list the expected future package manifest areas:

- package_identity
- source_identity
- evidence_reference
- included_components
- excluded_components
- build_environment_assumptions
- reproducibility_notes
- non_deployment_boundary

## Non-Deployment Boundary Flags

The dry-run preview must explicitly include all of these as false:

- creates_package_archive
- publishes_artifacts
- creates_docker_image
- creates_git_tag
- creates_github_release
- deploys
- modifies_ci
- writes_release_state_to_database
- promotes_environment

## Validation Expectations

The dry-run generator must have tests if implementation exists.

Tests must verify:
- dry-run status is true
- package status is preview
- non-deployment flags are false
- expected manifest fields are present
- default output path is local and non-release
- no packaging or deployment behavior is represented as enabled

## Current Boundary

Mini-EPIC 32.9 introduces only:
- this dry-run contract
- a minimal local-only preview generator
- targeted tests for the dry-run preview structure
- EPIC 32 documentation alignment
- closure evidence

It does not introduce real release packaging.
