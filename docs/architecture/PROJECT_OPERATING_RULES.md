# Project Operating Rules

## Core Rules
- No EPIC is DONE without architecture document, implementation evidence, tests, and closure file.
- EPIC_TRACKER.md is updated only after meaningful work sessions.
- Architecture file must exist before deep implementation starts.
- Auto-detect scripts are advisory, not the final source of truth.
- Status must reflect repo reality, not intention.

## Status Rules
- NOT STARTED = no meaningful artifacts exist
- IN PROGRESS = work has started but architecture or core artifacts are incomplete
- PARTIAL = architecture exists and implementation/testing is incomplete
- DONE = architecture + code/tests + closure exist
- BLOCKED = manual status only; never auto-detected

## Naming Rules
- Architecture files live under docs/architecture/
- Closure files must be named EPIC_X_CLOSURE.md
- Manifest files must be named epic-XX.json
- Templates live under docs/architecture/templates/

## Workflow Rules
- Start EPIC -> create architecture doc
- During EPIC -> update tracker only after meaningful progress
- Finish EPIC -> create closure file
- Then move to next EPIC

## Repository Hygiene
- UTF-8 without BOM
- LF line endings preferred
- Avoid ad-hoc file naming
- Avoid manual status drift from repo reality