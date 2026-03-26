# STORAGE ORDERING GUARANTEE — InvoMatch

## Purpose

Define deterministic ordering rules for reconciliation runs.

This guarantees:

- stable pagination
- replay determinism
- audit reproducibility
- worker fairness

---

## Ordering Key

Runs MUST be ordered by:

1. created_at
2. run_id

Run_id acts as deterministic tie-breaker.

---

## Pagination Rule

Pagination MUST be based on:

- cursor or (created_at, run_id) tuple
- NOT offset-only pagination for large datasets

---

## Clock Skew Protection

Workers may create runs with identical timestamps.

Ordering MUST remain stable.

---

## Contract

Any change to ordering logic requires:

- ordering contract tests
- pagination replay test
- concurrency insert ordering test

Storage ordering is part of external API stability.