# Run Detail Page — Flow Definition

## Purpose
Provide a complete product-facing view of a single run.

This page is the primary operational surface for understanding run state,
review state, actionability, and export readiness.

---

## Primary Data Sources

- GET /api/reconciliation/runs/{run_id}/view
- GET /runs/{run_id}/review
- GET /runs/{run_id}/export

---

## Page Sections

### 1. Run Status Section
Derived from:
- run

Displays:
- run_id
- status
- created_at
- updated_at
- operational metadata if exposed

---

### 2. Match Summary Section
Derived from:
- match_summary

Displays:
- backend-provided match summary only

No UI-side recomputation is allowed.

---

### 3. Review Summary Section
Derived from:
- review_summary

Displays:
- backend-provided review summary
- review-required visibility

---

### 4. Review Items Section
Derived from:
- GET /runs/{run_id}/review

Displays:
- list of review items
- review item status
- review item identifiers
- relevant review metadata if exposed

This section is visibility-only unless action execution is triggered.

---

### 5. Export Summary Section
Derived from:
- export_summary
- GET /runs/{run_id}/export

Displays:
- export readiness
- export not ready state
- artifacts if available

---

### 6. Action Surface
Derived from:
- backend action endpoints and backend response behavior

Displays:
- action triggers
- action execution result
- rejection messages

The UI does not determine final validity of any action.

---

## UI States

### Loading
- show loading indicator for page-level fetch

### Loaded
- show sections in deterministic order

### Partial Error
- if one secondary surface fails, show page with visible degraded section
- do not invent replacement data

### Error
- if primary run view fails, show blocking error state

### Refreshing
- after action execution, re-fetch page data

---

## Fetch Strategy

### Initial Load
Fetch:
1. Run View
2. Review
3. Export

Recommended behavior:
- treat Run View as primary dependency
- treat Review and Export as secondary dependencies

---

## Behavior Rules

- UI does not reconstruct product logic
- UI does not derive run lifecycle rules
- UI does not derive export readiness
- UI does not derive review eligibility
- UI only renders backend truth

---

## Action Execution Flow

When an action is triggered:

1. POST /runs/{run_id}/actions
2. show success or rejection result
3. re-fetch:
   - GET /api/reconciliation/runs/{run_id}/view
   - GET /runs/{run_id}/review
   - GET /runs/{run_id}/export

No optimistic state mutation is allowed.

---

## Constraints

- no frontend state machine
- no hidden action gating
- no derived summaries
- no synthetic statuses
- no cached fake state after action

---

## Output

This page must provide a human-usable operational view of:
- current run truth
- current review truth
- current export truth
- allowed interaction entry points

---

## Key Principle

Run Detail is the system truth page.

It must reflect backend product read models clearly and directly.
