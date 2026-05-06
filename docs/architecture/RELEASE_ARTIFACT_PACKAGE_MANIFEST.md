# Release Artifact Package Manifest

## Status

Defined for future release packaging.

This document defines the release artifact/package boundary and the expected package manifest format for InvoMatch.

It does not create a package, deployment, tag, GitHub Release, published artifact, promotion workflow, runtime release registry, or database-backed release evidence store.

## Purpose

A future InvoMatch release package must be a bounded, inspectable, reproducible handoff unit.

The package is not just a build output. It is a release candidate bundle whose identity, source, evidence, validation state, included components, exclusions, and non-deployment boundary are explicitly declared.

The package manifest is the canonical document that explains what the package claims to contain and what it deliberately does not claim to do.

## Release Artifact Boundary

A future InvoMatch release artifact/package means a controlled bundle prepared from a specific source revision and associated with a specific release candidate evidence index.

The package boundary must separate:

- source identity
- build/runtime components
- validation evidence
- generated export artifacts
- deployment environments
- operational runtime state
- promotion decisions

A package may contain buildable source snapshots, generated build outputs, evidence references, documentation snapshots, and release metadata.

A package must not imply that deployment, production promotion, semantic version tagging, rollback support, or public release publishing has occurred.

## Relationship to the Evidence Index

Every future package manifest must reference a release candidate evidence index.

The evidence index remains the structured record of validation evidence.

The package manifest must not duplicate all evidence content. Instead, it must identify:

- which evidence index applies
- which validation run or validation record supports the package
- whether validation passed, failed, was partial, or was not executed
- which evidence files are related to the package boundary
- whether any evidence was excluded from the package itself but referenced externally

The package manifest is the package identity and boundary record.

The evidence index is the validation evidence map.

They are related but not interchangeable.

## Required Package Manifest Fields

A future package manifest must include the following fields.

### Package Identity

The manifest must identify the package without relying only on filenames.

Required fields:

- package_id
- package_name
- package_type
- package_manifest_version
- package_created_at
- release_candidate_id
- release_identity
- package_status

Example:

~~~yaml
package_identity:
  package_id: invomatch-rc-local-001
  package_name: InvoMatch Release Candidate Package
  package_type: release-candidate
  package_manifest_version: 1
  package_created_at: 2026-05-06T00:00:00Z
  release_candidate_id: rc-local-001
  release_identity:
    release_name: local-release-candidate
    release_channel: local
    release_version: 0.0.0-rc-local
  package_status: draft
~~~

### Source Identity

The manifest must bind the package to an exact source state.

Required fields:

- source_commit_sha
- source_branch
- source_ref
- repository_url
- working_tree_state
- generated_from_clean_tree

Example:

~~~yaml
source:
  repository_url: https://github.com/ahabibian/InvoMatch.git
  source_commit_sha: "<commit-sha>"
  source_branch: main
  source_ref: refs/heads/main
  working_tree_state: clean
  generated_from_clean_tree: true
~~~

### Evidence Reference

The manifest must identify the evidence index and validation result that support the package.

Required fields:

- evidence_index_path
- evidence_index_version
- validation_status
- validation_summary_reference
- validation_executed_at
- validation_scope
- evidence_included_in_package
- evidence_referenced_only

Example:

~~~yaml
evidence:
  evidence_index_path: docs/architecture/RELEASE_CANDIDATE_EVIDENCE_INDEX.md
  evidence_index_version: 1
  validation_status: passed
  validation_summary_reference: docs/architecture/MINI_EPIC_32_7_CLOSURE.md
  validation_executed_at: 2026-05-06T00:00:00Z
  validation_scope:
    - documentation-format-check
  evidence_included_in_package:
    - docs/architecture/RELEASE_CANDIDATE_EVIDENCE_INDEX.md
  evidence_referenced_only:
    - docs/architecture/evidence/
~~~

### Included Components

The manifest must explicitly declare what is inside the future package boundary.

Allowed examples:

- backend source files
- backend tests
- frontend source files
- architecture documentation
- release pipeline documentation
- evidence index
- selected validation logs
- package manifest
- static frontend build output, if intentionally produced in a future packaging step

Example:

~~~yaml
included_components:
  backend_source:
    included: true
    path: src/
  backend_tests:
    included: true
    path: tests/
  frontend_source:
    included: true
    path: ui/invomatch-ui/src/
  architecture_docs:
    included: true
    path: docs/architecture/
  evidence_index:
    included: true
    path: docs/architecture/RELEASE_CANDIDATE_EVIDENCE_INDEX.md
  package_manifest:
    included: true
    path: docs/architecture/RELEASE_ARTIFACT_PACKAGE_MANIFEST.md
~~~

### Excluded Components

The manifest must explicitly declare what is outside the package boundary.

Required exclusions:

- local runtime databases
- local output artifacts unless intentionally included as evidence
- developer machine caches
- virtual environments
- node_modules
- Docker images
- deployment credentials
- production/staging environment state
- GitHub Release objects
- semantic version tags
- rollback state
- promotion records

Example:

~~~yaml
excluded_components:
  local_runtime_databases:
    excluded: true
    examples:
      - output/local/reconciliation_runs.sqlite3
      - output/local/review_store.sqlite3
      - output/local/exports/export_artifacts.sqlite3
  dependency_caches:
    excluded: true
    examples:
      - .venv/
      - node_modules/
  deployment_artifacts:
    excluded: true
    examples:
      - Docker images
      - Kubernetes manifests
      - environment promotion records
  public_release_objects:
    excluded: true
    examples:
      - GitHub Releases
      - semantic version tags
~~~

### Build Environment Assumptions

The manifest must record assumptions needed to reproduce or inspect the package.

Required fields:

- operating_system_family
- python_version
- node_version
- npm_version
- package_manager_assumptions
- environment_variables_required
- external_services_required
- database_assumptions

Example:

~~~yaml
build_environment:
  operating_system_family: Windows
  shell: PowerShell
  python_version: "3.14"
  node_version: "24.x"
  npm_version: "11.x"
  package_manager_assumptions:
    python: pip
    frontend: npm
  environment_variables_required:
    - PYTHONPATH=src
  external_services_required: []
  database_assumptions:
    runtime_database_creation: local-only
    packaged_database_state: excluded
~~~

### Reproducibility Notes

The manifest must explain what can and cannot be reproduced.

Required fields:

- reproducible_from_commit
- validation_reproducibility
- generated_artifact_reproducibility
- local_machine_dependency_notes
- known_non_reproducible_items

Example:

~~~yaml
reproducibility:
  reproducible_from_commit: true
  validation_reproducibility: command-based
  generated_artifact_reproducibility: future-packaging-step-required
  local_machine_dependency_notes:
    - Python and Node versions must be compatible with the recorded validation environment.
    - Local runtime databases are excluded and must not be treated as package inputs.
  known_non_reproducible_items:
    - timestamps
    - local absolute paths
    - machine-specific caches
~~~

### Non-Deployment Boundary

The manifest must explicitly state that package creation is not deployment.

Required fields:

- creates_deployment
- creates_tag
- creates_github_release
- publishes_artifact
- promotes_environment
- creates_rollback_point
- modifies_runtime_registry
- modifies_database_release_state

Example:

~~~yaml
non_deployment_boundary:
  creates_deployment: false
  creates_tag: false
  creates_github_release: false
  publishes_artifact: false
  promotes_environment: false
  creates_rollback_point: false
  modifies_runtime_registry: false
  modifies_database_release_state: false
~~~

## Manifest Format

The preferred future manifest format is YAML.

Reasons:

- readable in pull requests
- easy to diff
- easy to validate later
- suitable for CI-generated metadata
- compatible with future conversion to JSON if machine enforcement is needed

The future canonical filename should be:

~~~text
release-package-manifest.yaml
~~~

For Mini-EPIC 32.8, no actual manifest file is generated. This document only defines the future format.

## Future Validation Expectations

A future implementation that creates a package manifest should validate:

- required fields exist
- source commit SHA is present
- working tree was clean when generated
- evidence index reference exists
- validation status is explicit
- included and excluded components are both declared
- non-deployment boundary flags are all explicit
- package generation does not create tags, GitHub Releases, deployments, or published artifacts

## Current Mini-EPIC Boundary

Mini-EPIC 32.8 only defines the architecture boundary and manifest format.

It does not:

- build a package
- create Docker images
- generate a manifest artifact
- modify CI
- create semantic version tags
- create GitHub Releases
- publish artifacts
- implement rollback
- implement environment promotion
- change runtime behavior
- persist release metadata in a database