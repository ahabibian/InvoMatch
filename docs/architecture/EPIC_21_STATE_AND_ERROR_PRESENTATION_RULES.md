# State and Error Presentation Rules — EPIC 21

## Purpose
Define how the minimal product UI presents backend state and backend errors
without hiding, softening, or reinterpreting system truth.

---

## 1. Core Principle

The UI must present backend truth clearly.

The UI may translate backend state into human-readable display text,
but it must not invent alternative lifecycle meaning or synthetic product states.

---

## 2. State Presentation Rules

### queued
UI behavior:
- show queued state clearly
- communicate that the run exists but processing is not complete

UI must not:
- display completion-related controls
- imply review or export availability unless backend exposes it

---

### processing
UI behavior:
- show processing state clearly
- show that the run is in progress

UI must not:
- reinterpret processing as success
- imply final readiness
- hide that processing is incomplete

---

### review_required
UI behavior:
- show review-required state clearly
- expose review surface
- expose action surface if operator interaction is supported

UI must not:
- imply automatic resolution
- suppress review visibility
- invent a completed state

---

### completed
UI behavior:
- show completed state clearly
- expose export surface according to backend truth
- continue to show backend-provided summaries

UI must not:
- assume export exists if export surface says otherwise
- hide historical review context if still relevant in backend view

---

### failed
UI behavior:
- show failed state clearly
- preserve backend-provided context if available
- keep visible that the run did not complete successfully

UI must not:
- soften failure into a neutral state
- auto-convert failed into retrying unless backend explicitly changes state
- imply operator success when the backend says failed

---

## 3. Loading Rules

### Initial Page Loading
UI may:
- show page-level loading indicator
- delay section rendering until primary dependency is available

UI must not:
- show invented placeholder business state
- display guessed summaries before backend response

---

### Section-Level Loading
For secondary sections such as review or export:
- show localized loading indicator
- keep page structure stable when possible

---

### Refresh Loading
After action execution or operator refresh:
- show non-destructive refresh state
- avoid clearing already visible truth prematurely

---

## 4. Error Categories

### Input Validation Error
Source:
- POST /input/json
- POST /input/file

UI behavior:
- display validation/rejection message clearly
- display details if provided
- preserve operator ability to correct and resubmit

---

### Blocking Page Error
Source:
- primary page dependency failure, especially Run View failure

UI behavior:
- show clear blocking error
- do not render fake operational truth

---

### Section Degradation Error
Source:
- secondary dependency failure, such as review or export fetch failure

UI behavior:
- show degraded section clearly
- preserve rest of page if primary truth is still available
- do not replace missing data with guesses

---

### Action Rejection Error
Source:
- POST /runs/{run_id}/actions

UI behavior:
- show rejection clearly
- show reason if provided
- preserve current backend-derived visible state

UI must not:
- convert rejection into warning-only success
- hide rejection because action was operator-initiated

---

### Network / Transport Error
Source:
- connectivity or transport failure before meaningful backend response

UI behavior:
- show request failure clearly
- distinguish it from backend business rejection where possible

---

## 5. Error Presentation Rules

The UI may normalize visual presentation,
but it must preserve semantic difference between:

- validation failure
- business rejection
- run failure
- section fetch failure
- transport/network failure

These must not be collapsed into one generic product message.

---

## 6. Degraded State Rules

If a secondary surface fails:

- keep primary run truth visible if available
- mark the affected section as unavailable or failed to load
- avoid removing the whole page unnecessarily

If the primary truth surface fails:

- do not render a partially invented detail page
- show blocking page error

---

## 7. Operator Clarity Rules

At all times, the operator must be able to understand:

- what the current run state is
- whether the page is loading or the run is processing
- whether review is required
- whether export is available
- whether an action failed due to backend rejection or network failure

The UI must not merge these into ambiguous messaging.

---

## 8. Forbidden UI Behavior

The UI must not:

- invent intermediate business states
- hide failure to make the interface look smoother
- convert backend rejection into soft success
- show export readiness without backend confirmation
- show completed semantics while backend state is still processing
- erase visible truth during refresh without reason

---

## 9. Key Principle

State and error presentation are part of product integrity.

The UI must reveal operational truth clearly,
even when that truth is incomplete, degraded, rejected, or failed.
