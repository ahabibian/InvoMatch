# Run List Page — Flow Definition

## Purpose
Provide a high-level operational overview of all runs.

---

## Data Source
GET /runs

---

## Data Fields

- run_id
- status
- created_at
- updated_at
- summary

---

## UI Representation

Table view:

Columns:
- Run ID
- Status
- Created At
- Updated At
- Summary (flattened)

---

## UI States

### Loading
- show loading indicator

### Loaded
- show table

### Empty
- show "no runs available"

### Error
- show error message

---

## Behavior Rules

- UI does not aggregate or compute data
- UI does not interpret status beyond display
- UI does not fetch additional details

---

## Interaction

### Row Click
- navigate to Run Detail Page

---

## Sorting / Filtering (Optional Future)

Not part of EPIC 21 baseline

---

## Constraints

- no match-level data
- no review-level data
- no export-level data
- no derived metrics

---

## Output

- list of runs
- navigation entry point to detail

---

## Key Principle

This page is a gateway, not an analysis surface.
