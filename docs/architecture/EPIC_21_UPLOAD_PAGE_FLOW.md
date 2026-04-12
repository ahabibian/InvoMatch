# Upload Page — Flow Definition

## Purpose
Allow operator to submit input into the system via JSON or file.

---

## Data Sources
- No initial data fetch required

---

## User Inputs
- JSON payload (textarea)
- File upload

---

## API Calls
- POST /input/json
- POST /input/file

---

## UI States

### Idle
- empty input
- submit disabled or enabled

### Submitting
- loading indicator
- disable submit

### Success
- show run_id
- show status

### Error
- show validation errors
- show rejection message

---

## Behavior Rules

- UI does not validate business rules
- UI sends raw input to backend
- backend returns acceptance or rejection

---

## Output

On success:
- run_id displayed
- optional navigation to Run Detail

On failure:
- error message shown

---

## Post-Action Flow

Option A:
- stay on page

Option B (recommended):
- navigate to Run Detail

---

## Constraints

- no transformation of input
- no interpretation of response
- no hidden retry logic
