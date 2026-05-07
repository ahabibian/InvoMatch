# Mini-EPIC 32.16 Closure - Release Manifest CLI Real Failure Evidence Verification

## Status

Closed.

## Context

Mini-EPIC 32.16 hardened the release package manifest dry-run evidence model by verifying the deterministic CLI failure contract through real command-line execution.

Mini-EPIC 32.15 had already verified clean-state CLI success behavior. Mini-EPIC 32.16 verified the opposite path: an invalid dry-run manifest schema condition fails safely before any preview file is written.

This was an evidence hardening step only.

It introduced no new product behavior, no package generation, no deployment behavior, and no public CLI semantics.

## Confirmed Starting State

Repository state before failure evidence capture:

- branch: main
- branch alignment: up to date with origin/main
- working tree: clean
- latest commit: d8eb170 docs: verify release manifest dry-run cli clean-state evidence

Relevant previous commits:

- 8a94841 test: define release manifest dry-run cli success contract
- 25366b5 docs: finalize mini epic 32.13 clean-state evidence
- a8a0265 test: define release manifest dry-run cli failure contract

The starting state confirmed that Mini-EPIC 32.15 was the latest pushed state before Mini-EPIC 32.16 evidence capture.

## Existing Failure Mechanism Review

The existing failure-path mechanism was reviewed in:

- tests/test_release_manifest_dry_run.py
- scripts/release_manifest_dry_run.py

The existing test-supported failure path monkeypatches build_manifest_preview to return an invalid manifest and then executes the CLI entrypoint through release_manifest_dry_run.main(...).

The deterministic schema failure used by the existing contract is:

    manifest schema invalid: dry_run must be true

The CLI implementation catches ReleaseManifestDryRunError, writes the validation message to stderr, returns exit code 1, and does not write preview output when validation fails before write.

No public CLI flag, schema behavior, product behavior, or package behavior was changed for this Mini-EPIC.

## Real Command-Line Failure Evidence

A real command-line execution was performed using python -c from PowerShell.

The command imported the existing release manifest dry-run CLI module, patched build_manifest_preview inside the command-line Python process to produce the same invalid manifest condition already covered by tests, and executed release_manifest_dry_run.main(...) with --write-preview and an explicit requested output path.

The execution captured:

- stdout: output/local/mini_epic_32_16_failure_evidence/failure_stdout.txt
- stderr: output/local/mini_epic_32_16_failure_evidence/failure_stderr.txt
- exit code: output/local/mini_epic_32_16_failure_evidence/failure_exit_code.txt
- requested preview target: output/local/mini_epic_32_16_failure_evidence/should_not_exist.json
- default preview target: output/local/release_manifest_dry_run/package_manifest_preview.json

The generated evidence files are local-only evidence artifacts.

They are not release artifacts and are not included in package semantics.

## Real Failure Evidence Results

The real CLI failure scenario produced:

- exit code: 1
- stdout: empty
- stderr: manifest schema invalid: dry_run must be true
- requested preview written: false
- default preview written: false

Verified failure contract:

| Check | Result |
|---|---|
| Real command-line failure scenario executed | Passed |
| Exit code was non-zero | Passed |
| Stdout was empty | Passed |
| Stderr contained deterministic validation output | Passed |
| Stderr contained expected prefix manifest schema invalid: | Passed |
| Requested preview file was not written | Passed |
| Default preview file was not written | Passed |

## Targeted Test Evidence

Command:

    $env:PYTHONPATH = "src"
    pytest -q tests\test_release_manifest_dry_run.py --basetemp=.pytest_tmp

Result after real failure evidence capture:

    23 passed in 0.16s

## Files Changed

- docs/architecture/EPIC_32_RELEASE_PIPELINE.md
- docs/architecture/MINI_EPIC_32_16_CLOSURE.md

No source code, tests, CI workflow, frontend, schema, package output behavior, release identity behavior, or runtime behavior was changed.

## Non-Deployment Boundary

Mini-EPIC 32.16 did not introduce:

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
- new public CLI flags

## Closure Criteria Review

| Closure Criterion | Status |
|---|---|
| Clean repository state verified before failure evidence capture | Passed |
| Real CLI failure scenario executed | Passed |
| Failure scenario returned non-zero exit code | Passed |
| Failure scenario emitted nothing to stdout | Passed |
| Failure scenario emitted deterministic validation failure output to stderr | Passed |
| Stderr included manifest schema invalid: | Passed |
| No requested preview file was written | Passed |
| No default preview file was written | Passed |
| Targeted tests passed | Passed |
| EPIC 32 documentation updated | Passed |
| Mini-EPIC 32.16 closure document created | Passed |
| No real package/deployment/tag/release/registry/database/CI/frontend change introduced | Passed |

## Final Status

Mini-EPIC 32.16 is closed as an evidence-only hardening step.

The release package manifest dry-run CLI now has documented real command-line evidence for both clean success behavior and deterministic schema failure behavior.
