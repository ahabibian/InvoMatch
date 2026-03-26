# FEEDBACK SQLITE STORAGE

## Goal
Provide a SQLite-backed persistence layer for feedback intelligence using the same architectural pattern already present in the project.

## Alignment with current repository architecture
The current codebase uses Python-managed SQLite schema bootstrap instead of a dedicated numbered migration runner. Feedback persistence follows that same pattern for now.

## Storage decisions
- correction events are immutable inserts
- learning signals are immutable inserts
- candidate rule recommendations are versioned append-only rows
- promotions are separate audit rows
- rollbacks are separate audit rows

## Why recommendation rows are versioned
Recommendation status changes must not overwrite prior history. Approval, activation, rejection, and rollback must remain reconstructable from database state alone.

## Deterministic ordering
- correction events: occurred_at_utc, correction_id
- learning signals: extracted_at_utc, signal_id
- recommendations: latest version per recommendation_id, then created_at_utc, recommendation_id

## Current limitations
- schema bootstrap is embedded in Python service code
- no global migration runner yet
- no bulk transaction orchestration yet
- no Postgres implementation yet

## Next hardening step
When the project gains a formal migration system, the schema in sqlite_feedback_repository.py should be moved into the canonical migration chain without changing the logical storage contract.