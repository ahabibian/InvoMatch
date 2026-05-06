# Mini-EPIC 32.13 Closure - Release Package Manifest Preview CLI Failure Contract

## Status

Closed.

## Context

Mini-EPIC 32.12 added local schema validation for the release package manifest dry-run preview.

That validation protected the manifest structure before stdout output or optional local preview writing, but the command-line failure boundary still needed to be defined and tested.

Mini-EPIC 32.13 closes that gap by defining how schema validation failures must behave at the CLI boundary.

## Goal

Define and validate the CLI failure contract for the release package manifest dry-run generator.

The goal was to ensure schema validation failures are surfaced clearly and safely at the command-line boundary without creating any release artifact.

## Scope Completed

This Mini-EPIC completed the following:

- inspected the current dry-run generator behavior
- kept the behavior local-only
- introduced a small internal CLI runner boundary
- kept schema validation before stdout and file writing
- converted known dry-run validation failures into deterministic CLI stderr output
- returned a non-zero exit code for schema validation failures
- ensured invalid manifests do not produce stdout JSON
- ensured invalid manifests do not write preview files
- added targeted tests for CLI failure behavior
- preserved valid preview behavior
- updated dry-run contract documentation
- updated EPIC 32 release pipeline documentation

## Implementation Summary

### CLI Boundary

The dry-run generator now separates CLI execution into:

- an internal runner that parses arguments, builds the manifest, validates it, and writes success output
- a public `main()` boundary that catches `ReleaseManifestDryRunError`

Known dry-run validation errors are converted into:

- exit code `1`
- deterministic stderr text
- no stdout JSON
- no preview file output

### Failure Contract

On schema validation failure, the CLI must:

- return a non-zero exit code
- write the deterministic error text to stderr
- write nothing to stdout
- write no preview output file
- remain local-only

The deterministic schema validation prefix remains:

~~~text
manifest schema invalid:
~~~

Example failure output:

~~~text
manifest schema invalid: dry_run must be true
~~~

### Success Contract Preserved

Valid dry-run preview behavior remains unchanged:

- stdout mode emits valid JSON
- `--write-preview` writes only the requested local preview file
- `dry_run` remains `true`
- `package_status` remains `preview`
- no real package is created

## Files Changed

- `scripts/release_manifest_dry_run.py`
- `tests/test_release_manifest_dry_run.py`
- `docs/architecture/PACKAGE_MANIFEST_DRY_RUN_CONTRACT.md`
- `docs/architecture/EPIC_32_RELEASE_PIPELINE.md`
- `docs/architecture/MINI_EPIC_32_13_CLOSURE.md`

## Validation Evidence

### Targeted Release Manifest Dry-Run Tests

Command:

~~~powershell
cd C:\dev\InvoMatch
$env:PYTHONPATH = "src"
pytest -q tests\test_release_manifest_dry_run.py --basetemp=.pytest_tmp
~~~

Result:

~~~text
21 passed in 2.69s
~~~

### Valid CLI Stdout Preview Check

Command:

~~~powershell
cd C:\dev\InvoMatch
python scripts\release_manifest_dry_run.py | python -m json.tool | Select-String -Pattern '"dry_run": true|"package_status": "preview"' -Context 0,0
~~~

Observed output:

~~~text
    "dry_run": true,
        "package_status": "preview",
    "package_status": "preview",
~~~

## Exit Criteria Review

| Exit Criteria | Status |
|---|---|
| CLI schema failure behavior is documented | Met |
| Validation failures return non-zero exit code | Met |
| Validation failures are written to stderr | Met |
| Invalid manifests do not produce stdout JSON | Met |
| Invalid manifests do not write preview files | Met |
| Targeted tests pass | Met |
| `dry_run` remains true for valid preview | Met |
| `package_status` remains preview for valid preview | Met |
| No real package/deployment/tag/release is created | Met |
| EPIC 32 documentation is updated | Met |
| Mini-EPIC 32.13 closure document is created | Met |

## Explicit Non-Goals Preserved

This Mini-EPIC did not introduce:

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

## Closure Decision

Mini-EPIC 32.13 is closed.

The release package manifest dry-run generator now has a deterministic command-line failure contract for schema validation failures while preserving the local-only preview boundary.

## Final Clean-State Verification After Commit and Push

### Commit and Push Evidence

Implementation commit:

~~~text
a8a0265 test: define release manifest dry-run cli failure contract
~~~

Push result:

~~~text
a796b7c..a8a0265  main -> main
~~~

### Final Repository State

Command:

~~~powershell
cd C:\dev\InvoMatch
git status
~~~

Result:

~~~text
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
~~~

### Latest Commit Verification

Command:

~~~powershell
git --no-pager log --oneline -5
~~~

Result:

~~~text
a8a0265 (HEAD -> main, origin/main, origin/HEAD) test: define release manifest dry-run cli failure contract
a796b7c docs: finalize mini epic 32.12 clean-state evidence
62c7a08 test: add package manifest dry-run schema validation
7237845 docs: finalize mini epic 32.11 clean-state evidence
116ca34 test: define deterministic package manifest content contract
~~~

### Final Closure Evidence

Mini-EPIC 32.13 is committed, pushed, and clean.

No real package, archive, artifact publishing, Docker image, tag, GitHub Release, deployment, CI workflow change, runtime release registry, database persistence, rollback behavior, frontend UI change, or environment promotion was introduced.
