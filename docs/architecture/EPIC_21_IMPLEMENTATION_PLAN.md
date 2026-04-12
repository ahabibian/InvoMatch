# EPIC 21 — Minimal Product UI Implementation Plan

## Purpose
Define the narrowest implementation path for delivering a usable operator-facing UI
without introducing unnecessary frontend architecture or duplicated product logic.

---

## 1. Implementation Goal

Deliver a minimal human-facing UI that supports:

- input submission
- run listing
- run detail visibility
- review visibility
- action execution
- export visibility / access

The implementation must remain thin and backend-aligned.

---

## 2. Implementation Constraints

The implementation must not introduce:

- frontend business rules
- frontend lifecycle state machine
- client-side action authority
- complex caching
- optimistic updates
- advanced global state management
- design system expansion
- analytics / telemetry work beyond scope

---

## 3. Recommended Technical Shape

When environment is ready:

- React
- Vite
- TypeScript

Recommended structure:

- src/services/api.ts
- src/pages/UploadPage.tsx
- src/pages/RunListPage.tsx
- src/pages/RunDetailPage.tsx
- src/components/RunTable.tsx
- src/components/ReviewPanel.tsx
- src/components/ActionPanel.tsx
- src/components/ExportPanel.tsx

Optional:
- basic routing
- minimal shared layout shell

---

## 4. Layering Rules

### services/api.ts
Responsibility:
- HTTP requests
- response parsing
- normalized API errors

Must not:
- decide business flow
- cache product logic
- derive product state

---

### pages/*
Responsibility:
- orchestrate page-level fetching
- connect API calls to visible page state
- trigger refresh after user actions

Must not:
- duplicate backend rules
- derive alternative product truth

---

### components/*
Responsibility:
- render provided data
- collect operator input for actions

Must not:
- fetch hidden business dependencies
- reconstruct summaries
- mutate product truth locally

---

## 5. Delivery Sequence

### Phase 1 — Environment Preparation
- install Node.js / npm
- scaffold Vite React TypeScript project
- establish minimal folder structure

Exit condition:
- project boots locally

---

### Phase 2 — API Client
- implement api.ts
- confirm endpoint wiring for:
  - input submission
  - run list
  - run view
  - review
  - actions
  - export

Exit condition:
- thin API layer exists
- no business logic in client layer

---

### Phase 3 — Upload Page
- implement JSON submit
- implement file submit
- show validation / rejection response
- show accepted run_id response

Exit condition:
- operator can submit input through UI

---

### Phase 4 — Run List Page
- fetch GET /runs
- render high-level run list
- support navigation into run detail

Exit condition:
- operator can inspect existing runs

---

### Phase 5 — Run Detail Page
- fetch run view
- fetch review surface
- fetch export surface
- render deterministic section layout

Exit condition:
- operator can inspect a single run truthfully

---

### Phase 6 — Review and Action Surface
- render review items
- submit action requests
- handle rejection visibly
- re-fetch after successful action

Exit condition:
- operator can perform controlled action flow

---

### Phase 7 — Export Surface
- render export status
- render artifacts if available
- expose download/access only when backend confirms it

Exit condition:
- operator can understand export availability truthfully

---

### Phase 8 — End-to-End Demo Hardening
- validate full product loop manually
- confirm no hidden UI-side rule drift
- confirm degraded states remain truthful

Exit condition:
- human can demo:
  input → run → review → action → export

---

## 6. Non-Goals During Implementation

Do not add during EPIC 21:

- pagination redesign
- filtering / search platform
- auth redesign
- responsive/mobile work
- dashboarding
- websocket / realtime subscriptions
- custom design framework
- offline support

---

## 7. Key Principle

Implementation must remain intentionally narrow.

This EPIC is about making the system usable by a human operator,
not about creating a frontend platform.
