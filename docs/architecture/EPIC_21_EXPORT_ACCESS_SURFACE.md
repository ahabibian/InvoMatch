# Export Access Surface — EPIC 21

## Purpose
Define how the UI exposes export readiness, export availability,
and export artifact access without introducing UI-side business logic.

---

## 1. Data Sources

Primary sources:
- GET /api/reconciliation/runs/{run_id}/view
- GET /runs/{run_id}/export

The UI must treat backend export state as the single source of truth.

---

## 2. Export Surface Responsibilities

The UI may:

- show export summary
- show export ready / not ready state
- show artifact list if available
- provide access to artifact download endpoints if exposed
- show backend-provided export metadata

The UI must not:

- derive export readiness from unrelated fields
- assume export is ready after run completion unless backend says so
- hide export-not-ready state
- fabricate artifact availability

---

## 3. Export States

### Not Ready
The UI must:

- show that export is not ready
- preserve clarity that export access is unavailable
- avoid showing fake download actions

### Ready
The UI must:

- show readiness clearly
- show artifact list if artifacts are available
- expose artifact access only when backend exposes it

### Error
The UI must:

- show export fetch failure clearly
- keep the rest of the page stable if primary run view is available
- avoid replacing export data with guesses

---

## 4. Artifact Visibility Rules

If backend returns artifacts, the UI may show:

- artifact identifier
- artifact name / filename if exposed
- artifact format if exposed
- artifact metadata if exposed
- download/access entry point if exposed

The UI must not invent:
- synthetic filenames
- inferred artifact formats
- inferred download readiness

---

## 5. Download / Access Rules

If a valid artifact access endpoint or link is provided by backend:

- UI may render a download/access control

If backend does not provide artifact access:

- UI must not render a fake download button
- UI may show that artifact access is unavailable

---

## 6. Refresh Behavior

Export surface must be refreshed:

- on initial page load
- after successful action execution
- after explicit operator refresh if available

Recommended post-action refetch:
- GET /api/reconciliation/runs/{run_id}/view
- GET /runs/{run_id}/export

The UI must not assume export state changed until backend confirms it.

---

## 7. Presentation Rules

The export surface should communicate:

- whether export exists
- whether export is ready
- whether artifacts exist
- whether artifact access is currently possible

This communication must be explicit and backend-aligned.

---

## 8. Operator Clarity Rules

The operator must be able to tell:

- export is not ready yet
- export is ready but no artifact is exposed yet
- export is ready and artifact is available
- export surface failed to load

These are distinct states and must not be collapsed into one vague UI message.

---

## 9. Constraints

- no UI-derived export lifecycle
- no inferred artifact generation state
- no hidden fallback download logic
- no fake success state after action execution
- no synthetic artifact list

---

## 10. Key Principle

The export surface must expose availability truthfully.

It must not imply that export exists, is ready, or is downloadable
unless the backend explicitly provides that truth.
