# EPIC 21 — Minimal Product UI (Operator Interface)

---

## 1. Objective

Introduce a minimal operator-facing interface that exposes the core product workflow in a controlled, deterministic, API-aligned way.

This interface must allow a human operator to:

- Submit input (JSON / file)
- Inspect runs
- Understand run status
- Review actionable items
- Trigger allowed actions
- Access export artifacts

The UI must enable a complete product loop:

input → run → review → action → export

---

## 2. Architecture Principles

### 2.1 Thin Client

The UI is a thin client:

UI = fetch → render → action → refresh

No business logic is implemented in the UI.

---

### 2.2 Backend as Source of Truth

- All state comes from backend APIs
- No UI-derived state machine
- No duplicated business rules
- No frontend validation beyond basic form handling

---

### 2.3 Product Contract Alignment

The UI strictly consumes:

- Product Contract v1
- Run View (EPIC 11)
- Action API (EPIC 7 & 15)
- Ingestion boundary (EPIC 20)

The UI does not reinterpret or reshape backend data.

---

## 3. Screen Map

### 3.1 Upload Screen

Purpose:
Submit input into the system.

Capabilities:
- JSON submission
- File upload
- Display validation errors
- Show created run_id on success

---

### 3.2 Run List Screen

Purpose:
Provide operational visibility of runs.

Fields:
- run_id
- status
- created_at
- updated_at
- high-level summary

No detailed data is shown here.

---

### 3.3 Run Detail Screen

Purpose:
Expose full product state using Run View.

Sections:
- Run status
- Match summary
- Review summary
- Export summary
- Metadata (if available)

This screen directly reflects backend read models.

---

### 3.4 Review Panel

Purpose:
Display review items for the run.

- List review items
- Show current status
- No decision logic in UI

---

### 3.5 Action Panel

Purpose:
Trigger user actions.

- Send actions to backend
- Display success or rejection
- Refresh run state after execution

UI does not determine action validity.

---

### 3.6 Export Panel

Purpose:
Expose export readiness and artifacts.

- Show readiness state
- List artifacts
- Provide download access if available

---

## 4. API to UI Mapping

### Upload

POST /input/json  
POST /input/file  

Response:
- run_id
- status

Errors:
- validation errors
- rejection messages

---

### Run List

GET /runs  

Fields:
- run_id
- status
- created_at
- updated_at
- summary

---

### Run Detail

GET /api/reconciliation/runs/{run_id}/view  

Fields:
- run
- match_summary
- review_summary
- export_summary

---

### Review

GET /runs/{run_id}/review  

Fields:
- items

---

### Actions

POST /runs/{run_id}/actions  

Response:
- success
- rejected
- reason

---

### Export

GET /runs/{run_id}/export  

Fields:
- ready
- artifacts

---

## 5. State Presentation Rules

| Backend State     | UI Behavior                |
|------------------|--------------------------|
| queued           | show queued              |
| processing       | show loading indicator   |
| review_required  | show review panel        |
| completed        | show export              |
| failed           | show error               |

UI only translates state, not modifies it.

---

## 6. Action Handling Rules

- UI sends all actions to backend
- Backend determines validity
- UI reflects response

On success:
- refetch run state

On rejection:
- display reason

No frontend-side action gating logic.

---

## 7. Error Handling Model

UI surfaces:

- input validation errors
- action rejection errors
- run failure state
- network errors

UI does not reinterpret errors.

---

## 8. Screen Flow

Upload → Run Created → Run List → Run Detail  
                                      ↓  
                                   Review  
                                      ↓  
                                   Action  
                                      ↓  
                                   Refresh  
                                      ↓  
                                   Export  

---

## 9. Implementation Plan

Phase 1:
- Scaffold UI project (React + Vite)
- Setup basic routing

Phase 2:
- Implement Upload Screen
- Implement Run List Screen

Phase 3:
- Implement Run Detail Screen
- Integrate Run View API

Phase 4:
- Implement Review Panel
- Implement Action Panel

Phase 5:
- Implement Export Panel

Phase 6:
- Wire full flow end-to-end

No overengineering, no advanced state management.

---

## 10. Test Strategy

Focus on:

- API integration correctness
- action execution flow
- state rendering correctness

Types:
- smoke tests (UI loads, API reachable)
- integration tests (API → UI)
- manual operator validation

No heavy frontend test suite required.

---

## 11. Closure Criteria

EPIC is complete only if:

- Input submission works via UI
- Runs are visible in UI
- Run detail reflects backend read models exactly
- Actions can be triggered safely
- Invalid actions are rejected correctly
- Export visibility is accurate
- No UI-side business logic exists
- Full loop is demoable by a human operator

---

## 12. Final Constraint

The UI must reveal system truth clearly.

It must not:

- hide backend state
- reinterpret business logic
- introduce alternative flows

Backend remains the single source of truth.
