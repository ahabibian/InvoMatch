# Mini-EPIC 32.15 Closure - Release Manifest CLI Clean-State Success/Failure Evidence Verification

## Status

Closed.

## Context

Mini-EPIC 32.14 closed the release package manifest dry-run CLI success contract.

The CLI already had:

- deterministic schema validation failure contract
- deterministic success contract
- stdout JSON mode
- explicit --write-preview mode
- stderr silence on success
- stderr-only deterministic validation failure output

Mini-EPIC 32.15 was created as an evidence hardening step to verify the real CLI behavior from a clean, pushed repository state.

This Mini-EPIC did not introduce product behavior changes.

## Confirmed Starting State

Repository state was verified before evidence capture.

Commands:

    git branch --show-current
    git status
    git status --short
    git --no-pager log --oneline -5
    python .\scripts\release_manifest_dry_run.py --help

Observed state:

    main
    On branch main
    Your branch is up to date with 'origin/main'.

    nothing to commit, working tree clean

Recent commits:

    8a94841 (HEAD -> main, origin/main, origin/HEAD) test: define release manifest dry-run cli success contract
    25366b5 docs: finalize mini epic 32.13 clean-state evidence
    a8a0265 test: define release manifest dry-run cli failure contract
    a796b7c docs: finalize mini epic 32.12 clean-state evidence
    62c7a08 test: add package manifest dry-run schema validation

CLI help confirmed the available options:

    usage: release_manifest_dry_run.py [-h] [--repo-root REPO_ROOT] [--write-preview] [--output OUTPUT]

## Goal

Verify the release package manifest dry-run CLI contract from a clean, pushed repository state using real command-line executions, capturing evidence that both stdout JSON mode and explicit write-preview mode remain deterministic outside isolated unit tests.

## Scope Completed

Completed scope:

- confirmed clean repository state before evidence capture
- executed stdout JSON preview mode through the real CLI
- captured stdout, stderr, and exit code for stdout JSON mode
- verified stdout JSON mode emitted valid JSON
- verified stdout JSON mode emitted nothing to stderr
- verified stdout JSON mode did not write the default preview file
- verified stdout JSON mode contained dry_run: true
- verified stdout JSON mode contained package_status: preview
- executed explicit --write-preview mode through the real CLI
- captured stdout, stderr, and exit code for write-preview mode
- verified the requested preview file was written
- verified the default preview file was not written
- verified stdout contained deterministic human-readable success output
- verified stdout did not contain manifest JSON
- verified stderr was empty
- verified the written preview file contained dry_run: true
- verified the written preview file contained package_status: preview
- re-ran targeted tests
- updated EPIC 32 documentation
- created this closure document

## Local Evidence Location

All generated evidence was kept local-only under:

    output/local/release_manifest_dry_run/mini_epic_32_15/

Evidence files:

    stdout_json_mode.exit_code.txt
    stdout_json_mode.stderr.txt
    stdout_json_mode.stdout.json
    write_preview_mode.exit_code.txt
    write_preview_mode.stderr.txt
    write_preview_mode.stdout.txt
    requested_package_manifest_preview.json

These files are local evidence only and are excluded from release package semantics.

## Real CLI Evidence - stdout JSON Preview Mode

Command shape:

    python .\scripts\release_manifest_dry_run.py --repo-root . 1> output\local\release_manifest_dry_run\mini_epic_32_15\stdout_json_mode.stdout.json 2> output\local\release_manifest_dry_run\mini_epic_32_15\stdout_json_mode.stderr.txt

Observed result:

    exit code: 0
    stderr length: 0
    dry_run: True
    package_status: preview
    default preview file written: False

Evidence files:

    stdout_json_mode.exit_code.txt      6 bytes
    stdout_json_mode.stderr.txt         0 bytes
    stdout_json_mode.stdout.json    10776 bytes

Conclusion:

stdout JSON preview mode behaves as contracted. It emits valid manifest JSON to stdout, emits nothing to stderr, returns exit code 0, and does not write a preview file unless explicitly requested.

## Real CLI Evidence - Explicit --write-preview Mode

Command shape:

    python .\scripts\release_manifest_dry_run.py --repo-root . --write-preview --output output\local\release_manifest_dry_run\mini_epic_32_15\requested_package_manifest_preview.json 1> output\local\release_manifest_dry_run\mini_epic_32_15\write_preview_mode.stdout.txt 2> output\local\release_manifest_dry_run\mini_epic_32_15\write_preview_mode.stderr.txt

Observed result:

    exit code: 0
    stderr length: 0
    stdout: Wrote dry-run package manifest preview to C:\dev\InvoMatch\output\local\release_manifest_dry_run\mini_epic_32_15\requested_package_manifest_preview.json
    requested preview file exists: True
    default preview file written: False
    stdout starts with JSON object: False
    stdout contains dry_run key: False
    dry_run: True
    package_status: preview

Evidence files:

    requested_package_manifest_preview.json   5387 bytes
    write_preview_mode.exit_code.txt             6 bytes
    write_preview_mode.stderr.txt                0 bytes
    write_preview_mode.stdout.txt              310 bytes

Conclusion:

Explicit write-preview mode behaves as contracted. It writes only the requested local preview file, emits deterministic human-readable success output to stdout, emits no manifest JSON to stdout, emits nothing to stderr, and returns exit code 0.

## Targeted Test Validation

Command:

    $env:PYTHONPATH = "src"
    pytest -q tests\test_release_manifest_dry_run.py --basetemp=.pytest_tmp

Result:

    .......................                                                                             [100%]
    23 passed in 0.36s

## Non-Goals Confirmed

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

## Exit Criteria Review

| Exit Criteria | Status |
|---|---|
| Clean repository state verified before evidence capture | Met |
| stdout JSON preview mode executed through real CLI | Met |
| stdout JSON preview mode returned exit code 0 | Met |
| stdout JSON preview mode emitted valid manifest JSON to stdout | Met |
| stdout JSON preview mode emitted nothing to stderr | Met |
| stdout JSON preview mode did not write preview files | Met |
| stdout JSON preview output contained dry_run: true | Met |
| stdout JSON preview output contained package_status: preview | Met |
| --write-preview mode executed through real CLI | Met |
| --write-preview mode returned exit code 0 | Met |
| --write-preview mode wrote only requested local preview file | Met |
| --write-preview mode emitted deterministic success message to stdout | Met |
| --write-preview mode emitted no manifest JSON to stdout | Met |
| --write-preview mode emitted nothing to stderr | Met |
| Written preview file contained dry_run: true | Met |
| Written preview file contained package_status: preview | Met |
| Targeted tests passed | Met |
| EPIC 32 documentation updated | Met |
| Mini-EPIC 32.15 closure document created | Met |
| No real package/deployment/tag/release/registry/database/CI/frontend change introduced | Met |

## Boundary Confirmation

The generated evidence remains local-only under output/local/ and is excluded from release package semantics.

No real release artifact, deployment, tag, GitHub Release, runtime registry entry, database state, CI workflow modification, frontend UI change, or package publishing behavior was introduced.

## Closure Decision

Mini-EPIC 32.15 is closed.

The release package manifest dry-run CLI contract has been verified through real command-line execution from a clean, pushed repository state.