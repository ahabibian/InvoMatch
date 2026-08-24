# Mini-EPIC 34.4 — Deployed End-to-End Pilot Validation

## Baseline and duplicate gate

Starting `main` is `6cbbfad60bd672792f744e76657dd9694ea70b04`, containing merged Mini-EPIC 34.3 and `PILOT_DURABLE_STATE_READY`. Repository inspection found contract-level Scenario 15 proof and the 34.3 Compose durability scenario, but no post-34.3 deployed proof traversing the production Nginx boundary through authentication, supported ingestion, durable run/match/review state, Review Queue, Match Detail, FTL contract, failure semantics, and routine recreation. No canonical 34.4 record existed.

## Runtime topology and identity

The validated deployment is the repository-controlled `docker-compose.pilot.yml` production-intent topology:

`controlled client → loopback:8080 Nginx → same-origin /api/* → private backend:8000 Uvicorn/FastAPI → application services → /var/lib/invomatch named volume`.

The frontend is the Node 24 production build copied into the Nginx image; no Vite server participates. The backend image uses Python 3.11. CI injects the exact tested GitHub SHA, ref, application version `0.1.0`, environment `production`, and validation status. Authenticated `GET /api/operations/release-identity` must report that exact SHA, version, and environment.

## Authentication and served UI proof

CI reaches `/` through port 8080, confirms the real root application mount and an Nginx response header, then requires successful `/health` and `/readiness`. A protected Review Queue request without a session returns 401. Invalid non-demo credentials return 401. An externally supplied temporary admin credential logs in through `/api/auth/login`; the backend issues the HttpOnly cookie and subsequent requests use that session. Logout revokes it and the same session then receives 401. The client re-authenticates without frontend bearer-token injection.

The production artifact is scanned to exclude both `VITE_API_AUTH_TOKEN` and the temporary credential. It must contain the compiled Review Queue, Match Detail, and Traceability surfaces. Runtime logs and the 34.3 backup are scanned for the temporary credential. Product responses expose user information and permissions, not the opaque session identifier.

## Exact Scenario 15 input and path

The supported authenticated ingestion endpoint receives:

- batch: `scenario-15-deployed`;
- invoice: `scenario-15-invoice`, 2026-08-24, EUR 125.50, reference `SCENARIO-15`;
- payments: `scenario-15-payment-a` and `scenario-15-payment-b`, each explicitly bound to `scenario-15-invoice`, EUR 125.50, with the same reference.

The legitimate ambiguity produces backend-owned `review_required` truth. The exact deployed path is:

`Pilot login → Nginx-served Pilot UI contract → POST /api/reconciliation/runs/ingest → reconciliation run → configured run and match stores → configured review store → GET /api/review/queue → real match_id handoff → GET /api/review/matches/{match_id}/detail → compiled MatchDetailPanel evidence/traceability presentation`.

No SQLite fixture editing or direct backend-port call is used for the primary proof.

## Persistence, queue, detail, and FTL truth

The scenario exercises the run store, match-record store, review store, audit/security evidence, and ingestion provenance under `/var/lib/invomatch`. The API must return the recorded run ID with `review_required` status. Review Queue must return an open case for that run with a non-empty backend-generated `match_id` and reason code. That exact ID—never a synthesized UI value—is used for Match Detail.

Match Detail must preserve the ID, open unresolved state, invoice identity, one of the real candidate payment identities, backend confidence strictly below certainty, at least status and review-reason evidence, source provenance, and `failure: null`. The compiled FTL surfaces consume and label this backend-owned data; no frontend recalculation is introduced.

A nonexistent match must return HTTP 404 with `match_not_found`, proving technical absence remains distinct from the valid unresolved business result. HTTP 200 is not interpreted as a financial match, missing data is not converted to zero, and confidence is not promoted to certainty.

## Routine recreation proof

After primary validation, CI executes `docker compose down` without deleting the state volume, recreates both services, waits for readiness, and re-authenticates as permitted by the ephemeral-session contract. It rereads the same run, queue, and Match Detail. Canonical sorted queue and detail JSON must be identical before and after recreation. The pre-existing 34.3 backup/clean-volume-restore gate remains in the shared workflow but is not claimed as new 34.4 scope.

## Browser validation level

The repository has no established browser automation framework. In accordance with the boundary, 34.4 does not add Playwright or Cypress. UI proof consists of the real production-served Nginx asset, real same-origin HTTP/API/session continuity, runtime response contracts, compiled Review Queue/Match Detail/Traceability surfaces, frontend lint, and production build. Manual visual refinement or a future browser automation enhancement is not a blocker to this controlled proof.

## Defect and bounded fix

Validation discovered two contract-integration defects. Normal reconciliation persisted review-required match records but did not materialize them into the configured Review Queue store. The bounded fix routes duplicate/partial match records through the existing `ReviewIntegrationService`, preserving generated match identity, invoice/payment identity, confidence, mismatch reason, candidates, and source-file provenance. `ReviewIntegrationService` now honors an explicitly supplied source reference. The supported ingestion payment model also omitted `invoice_id`, preventing the existing reconciliation engine from associating API-ingested payments with invoices; the bounded schema fix preserves that existing key through CSV materialization. No matching algorithm, financial rule, UI design, authentication architecture, or deployment platform changes.

Focused regression proves a real ambiguous reconciliation creates a durable queue row and Match Detail candidate with identity and provenance continuity. The complete backend, contract, operational, Scenario 15, frontend, compilation, Compose, restart, readiness, and whitespace gates remain mandatory.

## Verdicts

`DEPLOYED_PILOT_END_TO_END_VALIDATED_WITH_BOUNDED_FIXES`

`EPIC_34_READY_FOR_GO_LIVE_READINESS_CLOSURE`

No public deployment, DNS, certificate, cloud resource, or launch authorization occurs. EPIC 32 and EPIC 33 remain closed. Mini-EPIC 34.5 is not started. The only recommended next action is one narrowly controlled Mini-EPIC 34.5 go-live-readiness/closure boundary.
