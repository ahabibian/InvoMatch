# AGENTS.md

## Product intent
Invoice Intelligence is a lightweight, accurate, ERP-independent invoice reconciliation tool for SMEs and accounting firms.

## Non-goals
Do not turn this project into:
- a full accounting platform
- a bookkeeping system
- a payment execution system
- a dashboard-heavy demo app

## Architecture rules
- Keep the existing `src/invomatch` structure.
- Do not introduce a parallel top-level architecture like `app/`.
- Keep API layer thin.
- Keep business logic in services.
- Keep domain models independent from FastAPI routes.
- Keep matching logic deterministic and testable.
- Prefer small focused diffs.

## Technical rules
- Do not add Docker unless explicitly requested.
- Do not add ORM/database layers unless explicitly requested.
- Do not add OCR integrations unless explicitly requested.
- Do not add authentication unless explicitly requested.

## Quality rules
- Update tests when behavior changes.
- Preserve deterministic behavior.
- Avoid large restructuring.
- Prefer clarity over cleverness.
