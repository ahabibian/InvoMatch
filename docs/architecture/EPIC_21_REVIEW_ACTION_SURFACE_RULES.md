# Review / Action Surface Rules — EPIC 21

## Purpose
Define how the UI exposes review visibility and action execution
without duplicating backend product flow logic.

---

## 1. Review Surface

### Data Source
- GET /runs/{run_id}/review

### UI Responsibility
The UI may:

- display review items
- display review item status
- display review metadata if exposed
- show that review exists or is required

The UI must not:

- determine review eligibility
- infer hidden review rules
- compute review outcomes
- decide whether a run should be review_required

---

## 2. Action Surface

### Data Source
- POST /runs/{run_id}/actions

### UI Responsibility
The UI may:

- render available action entry points
- collect required operator input
- send action request payload
- display backend response
- trigger deterministic refresh

The UI must not:

- decide final action validity
- enforce product flow rules as source of truth
- mutate run state locally after action
- hide backend rejection

---

## 3. Action Rendering Rules

### Baseline Rule
Actions are rendered as UI entry points,
but backend remains the final authority.

### UI Allowed Behavior
The UI may:

- show action buttons
- disable buttons during active submission
- attach payload fields required for action execution

### UI Forbidden Behavior
The UI must not:

- invent new actions
- hide action rejection logic
- implement a frontend state machine
- assume action success before backend confirmation

---

## 4. Action Request Model

Each action request must be sent as:

- action_type
- payload

The UI is only responsible for request assembly.
The backend is responsible for business validation.

---

## 5. Success Behavior

When backend accepts the action:

1. show success response
2. re-fetch:
   - GET /api/reconciliation/runs/{run_id}/view
   - GET /runs/{run_id}/review
   - GET /runs/{run_id}/export
3. replace visible state with fresh backend state

No optimistic updates are allowed.

---

## 6. Rejection Behavior

When backend rejects the action:

The UI must:

- show rejection status
- show rejection reason if provided
- preserve current backend-derived visible state
- avoid synthetic fallback state

The UI must not:

- reinterpret rejection
- auto-retry silently
- convert rejection into fake success

---

## 7. Invalid Action Handling

If the operator triggers an invalid action:

- backend response must be displayed clearly
- current page state must remain stable
- operator must remain on the current page unless explicit navigation is needed

No UI-side attempt should be made to "fix" the action outcome.

---

## 8. Refresh Policy

### After Successful Action
Mandatory refetch of:
- run view
- review surface
- export surface

### After Rejected Action
Recommended behavior:
- preserve current state
- optionally re-fetch run view if backend may have changed related state

### During Refresh
- show non-destructive loading state
- do not clear current page content prematurely

---

## 9. Error Presentation

### Action Submission Error
Display:
- backend message
- transport/network error if request failed before backend response

### Review Fetch Error
Display:
- visible degraded section
- do not hide the full page if primary run view is still available

### Primary Page Integrity Rule
Run View remains the primary truth surface.
Secondary failures must not produce invented data.

---

## 10. Operator Experience Constraint

The operator must always be able to understand:

- what action was attempted
- whether it succeeded or failed
- what the current backend truth is after the attempt

The UI must never leave the operator in an ambiguous state.

---

## 11. Key Principle

Review and action surfaces are controlled interaction layers.

They expose backend truth and backend enforcement.
They do not replace them.
