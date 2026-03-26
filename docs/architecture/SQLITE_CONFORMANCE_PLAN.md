# SQLITE_CONFORMANCE_PLAN.md

## Status
Proposed

## Purpose

Define how the current SQLite-backed reconciliation run store will be brought into conformance with the backend-independent Run Store contract introduced in EPIC 2.

This document exists because the current implementation and the new persistence contract do not yet align one-to-one.

The goal is to close that gap deliberately, not implicitly.

---

## 1. Current Reality

The current SQLite implementation is located in:

- src/invomatch/services/run_store.py

The newly introduced persistence architecture is located in:

- src/invomatch/persistence/base.py
- src/invomatch/persistence/sqlite/run_store.py

At the moment, the real implementation still lives under services, while the persistence package contains architectural scaffolding only.

This means the repository is currently in a transition state.

---

## 2. Problem Statement

The current SQLite run store does not yet conform directly to the new backend-independent RunStore contract.

Mismatch areas:

1. Module location mismatch
2. Method shape mismatch
3. Model mismatch

This mismatch must be resolved before contract tests can become meaningful.

---

## 3. Architectural Decision

The contract introduced in EPIC 2 remains the target authority.

The existing SQLite implementation is treated as the migration source, not the final design authority.

---

## 4. Recommended Path

Contract-first incremental refactor.

- do not move files physically yet
- converge behavior first
- enable contract tests progressively

---

## 5. Exit Criteria

- SQLite backend satisfies RunStore contract
- lifecycle methods exist explicitly
- retry semantics durable
- terminal semantics explicit
- contract tests meaningful
- persistence architecture location aligned

---

## Summary

EPIC 2 is a convergence effort, not a rewrite effort.