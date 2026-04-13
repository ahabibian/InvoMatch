# EPIC 20 — Integration Repair Addendum

## Status
Post-closure integration repair identified during EPIC 21 implementation.

This is not a scope reopening of EPIC 20.
This is a repair record for an integration defect discovered when the EPIC 20 input boundary
was consumed by the EPIC 21 minimal product UI.

---

## 1. Defect Summary

During EPIC 21 implementation, the frontend began consuming:

- POST /api/reconciliation/input/json
- POST /api/reconciliation/input/file

The JSON input route was operational but not fully contract-consumable through OpenAPI.

### Observed defect
- `/api/reconciliation/input/json` did not expose a request body schema in OpenAPI / Swagger
- frontend UI could call the route, but the contract was not discoverable or self-describing
- this created ambiguity for UI payload construction and contract-driven consumption

---

## 2. Root Cause

The JSON route was implemented using raw request parsing:

- `request: Request`
- `payload = await request.json()`

Because the route did not declare a typed request body parameter,
FastAPI did not generate a `requestBody` definition in OpenAPI for this endpoint.

This caused Swagger to omit JSON request body shape for the route.

---

## 3. Repair Applied

### 3.1 JSON Route Contract Repair
The JSON input route was updated to declare an explicit body parameter:

- `payload: dict[str, Any] = Body(...)`

This change made the route contract visible to OpenAPI and therefore consumable by the EPIC 21 UI.

### 3.2 CORS Repair
During UI integration testing, browser-to-backend requests initially failed due to missing CORS configuration.

CORS middleware was added to the FastAPI application to allow:

- `http://localhost:5173`
- `http://127.0.0.1:5173`

This enabled the EPIC 21 frontend to call backend endpoints from the local Vite dev server.

---

## 4. Validation Evidence

After repair:

### JSON Contract Visibility
Swagger now exposes a request body for:

- POST /api/reconciliation/input/json

### UI Integration
The EPIC 21 Upload Page successfully submits valid JSON input to the repaired endpoint.

### Successful Product Response
A valid payload containing invoices and payments now returns:

- `status = run_created`
- non-null `input_id`
- non-null `ingestion_batch_id`
- non-null `run_id`
- empty `errors`

### Rejection Behavior
Invalid or structurally incorrect payloads still return product-safe failure responses,
including backend-derived error information.

This confirms that the repair improved contract visibility without bypassing backend truth.

---

## 5. Scope Interpretation

This repair does not change the closed implementation scope of EPIC 20.

It records a post-closure integration defect discovered only when EPIC 20 was exercised
through a real UI consumer in EPIC 21.

The repaired outcome is more accurate to the original EPIC 20 objective:

- externally reachable
- contract-driven
- API-consumable
- frontend-consumable

---

## 6. Final Note

EPIC 20 remains closed with this repair addendum recorded.

EPIC 21 continues from this corrected boundary.
