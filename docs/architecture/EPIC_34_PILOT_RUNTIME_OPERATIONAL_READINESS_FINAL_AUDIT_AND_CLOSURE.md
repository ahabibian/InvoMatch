# EPIC 34 — Pilot Runtime Operational Readiness Final Audit and Closure

## Boundary, baseline, and duplicate gate

Mini-EPIC 34.5 is the governance/readiness audit and terminal closure boundary for EPIC 34. The audited starting `main` is `9e94319fdad011a05ade938c1a322e74eaecfff8`, the squash merge of Mini-EPIC 34.4. The worktree was clean, local `main` was fast-forward aligned with `origin/main`, and the canonical records for Mini-EPICs 34.1, 34.2, 34.3, and 34.4 were present.

A repository-wide search found no existing EPIC 34 final closure, go-live-readiness closure, terminal closure, or equivalent post-34.4 runtime closure record. The duplicate gate is negative and permits this single canonical artifact. This audit does not implement another runtime phase, create Mini-EPIC 34.6, or start EPIC 35.

## Mini-EPIC 34.1 audit

Mini-EPIC 34.1 correctly recorded `READY_FOR_PILOT_RUNTIME_IMPLEMENTATION`. It identified a viable existing FastAPI/React/SQLite architecture and classified the missing production serving composition, deployed origin model, safe credential delivery, configured match persistence, complete mounted state boundary, recovery proof, and deployed Scenario 15 proof as implementation or operational-integration gaps. No original `PILOT_BLOCKER` remains silently unresolved.

| Original 34.1 blocker | Closed by | Final repository evidence | Status |
|---|---|---|---|
| Frontend/backend serving composition | 34.2 | `docker-compose.pilot.yml`, Nginx production frontend image, private Uvicorn backend, CI Compose smoke | CLOSED |
| Deployed origin/CORS model | 34.2 | Same-origin `/api/*` proxy, empty production CORS allow-list, no wildcard authenticated CORS | CLOSED |
| Unsafe demo credentials | 34.2 | Production/staging require explicit non-demo seed credentials and fail closed | CLOSED |
| Browser-bundled bearer credential | 34.2 | Server-issued HttpOnly session login; production bundle excludes `VITE_API_AUTH_TOKEN` | CLOSED |
| Match-record path/wiring gap | 34.3 | Configured `SqliteMatchRecordStore` is constructed and injected into application reconciliation | CLOSED |
| Durable state composition gap | 34.3 | Canonical paths are composed beneath mounted `/var/lib/invomatch` | CLOSED |
| Restart/backup/restore proof gap | 34.3 | Quiesced backup, clean restore, hashing, SQLite integrity, recreation and reread are CI-verified | CLOSED |
| Deployed Scenario 15 proof | 34.4 | Real Nginx/session/ingestion/reconciliation/queue/detail/FTL Compose path | CLOSED |

## Mini-EPIC 34.2 audit

Mini-EPIC 34.2 correctly concluded `PILOT_RUNTIME_COMPOSITION_READY`. The canonical runtime remains a reproducible Compose topology: Nginx serves the Node-built static UI and proxies same-origin API calls to an internal Python 3.11 Uvicorn/FastAPI service. No Vite development server participates. Only Nginx port 8080 is host-published; the backend uses Compose `expose` and is not normal pilot-user ingress.

Browser authentication uses a server-issued HttpOnly, strict session cookie. Backend permissions remain authoritative. Production/staging startup requires explicit non-demo credentials, rejects the committed development tokens, retains no frontend bearer-token dependency, and uses a narrow same-origin/CORS posture. `/readiness` fails non-2xx for material dependency/startup failure. Scheduler posture remains explicitly disabled and not required for the interactive pilot. Application version, exact commit, branch, environment, and validation identity remain inspectable. Inspection of the later 34.3 and 34.4 diffs found no regression of these guarantees.

## Mini-EPIC 34.3 audit

Mini-EPIC 34.3 correctly concluded `PILOT_DURABLE_STATE_READY`. The production application injects the configured match-record store; the pilot path does not use an import-time or module-relative match database. The configured ingestion root preserves source CSV and traceability provenance. Export-artifact metadata is wired to its configured SQLite repository, and finalized projections remain beneath the durable export root.

The coherent mounted state set is `/var/lib/invomatch`. It includes reconciliation runs, review state, match records, audit/security evidence, input sessions, ingestion provenance, export metadata, finalized projections, and retained artifacts/exports/uploads. Browser sessions, live metrics, stdout, images, and compiled frontend assets are ephemeral or reconstructable and are not canonical financial truth.

Backup is deliberately quiesced. The bounded operator tool verifies SQLite integrity, records inventory and hashes, refuses overwrite or malformed/corrupt input, restores only to clean state, and verifies the restored tree. Credentials, cookies, environment secrets, and TLS material are outside the state bundle. CI proves container recreation and clean-volume restore preserve readable canonical records. Mini-EPIC 34.4 retained and extended this same durability path without weakening it.

## Mini-EPIC 34.4 audit

Mini-EPIC 34.4 correctly concluded:

`DEPLOYED_PILOT_END_TO_END_VALIDATED_WITH_BOUNDED_FIXES`

and:

`EPIC_34_READY_FOR_GO_LIVE_READINESS_CLOSURE`

The real production-intent proof traverses:

`Nginx-served Pilot UI → same-origin API → session authentication → supported ingestion → reconciliation → durable run/match/review state → Review Queue → exact backend match_id → Match Detail → backend-owned FTL evidence/provenance`.

The deterministic ambiguous Scenario 15 input produces `review_required`. Review Queue exposes a real generated match identity and reason; Match Detail uses that exact handoff identity and returns backend-owned confidence, evidence, provenance, and unresolved state. A missing match returns explicit `match_not_found` technical failure. Routine recreation requires re-login, then returns identical canonical queue/detail JSON. The tested build identity is the exact CI commit. The bundle, runtime logs, and backup are checked for the temporary credential.

## Bounded-fix audit

The 34.4 fixes remain within EPIC 34 scope. Review-required reconciliation records are routed through the existing `ReviewIntegrationService` and existing Review Queue architecture. The pre-existing generated match ID, invoice/payment identities, confidence, mismatch reason, candidates, and source provenance are preserved. Adding optional `invoice_id` to the supported ingestion payment schema merely carries the existing association key into the CSV consumed by the existing reconciliation engine.

No matching algorithm, scoring threshold, financial rule, outcome classification, UI decision engine, authentication architecture, or deployment platform was introduced. The fixes close integration gaps and do not expand business semantics.

## Backend financial-truth authority audit

Backend financial-truth authority remains intact. Reconciliation services determine canonical outcomes and persist run, match, and review state. Backend query/read services construct confidence, review reason, evidence, provenance, and failure semantics. The frontend fetches and presents these fields, labels evidence and traceability as backend-owned, and explicitly states that Review Queue does not calculate confidence or synthesize rows. It does not determine match result, confidence, reason, evidence, provenance, or finality. EPIC 33 invariants are preserved and EPIC 33 remains terminally closed.

## Authentication and security audit

No real credential is committed. Production has no fallback to known demo credentials, and the production frontend contains neither a raw bearer credential nor the legacy bearer-token configuration. Login exchanges an externally injected credential for an opaque server-side session delivered by HttpOnly cookie. Invalid, expired, or inactive authentication fails; logout revokes the session; backend role/permission checks remain authoritative.

In-memory browser sessions intentionally disappear on runtime recreation and require re-login. They are not canonical business state. Persistent security and operational audit evidence remains in the configured audit database. Enterprise SSO and a managed secret platform are post-pilot enhancements, not controlled-pilot closure requirements.

## Runtime and network audit

The canonical topology remains:

`controlled client → Nginx serving boundary → internal FastAPI backend → durable application state`.

The backend port is private within Compose, production API calls are same-origin through Nginx, and authenticated wildcard CORS is not enabled. The validated topology uses loopback and does not require public exposure. Core runtime behavior has no silent outbound service dependency; network access is required only to obtain build dependencies/images in the build environment.

## Health and readiness audit

`/health` is a lightweight liveness surface. `/readiness` checks startup-repair state, configured critical SQLite stores, and required storage roots, returning HTTP 503 with bounded dependency identifiers when materially unavailable. Startup blocking states are surfaced and the Compose backend health check uses readiness. Liveness, application readiness, and financial reconciliation success remain distinct concepts.

## Durable-state inventory and classification

| State | Classification | Final disposition |
|---|---|---|
| Runs, reviews, matches | Canonical durable | SQLite beneath `/var/lib/invomatch`; backed up and restored |
| Audit/security evidence and input sessions | Canonical durable evidence | SQLite beneath `/var/lib/invomatch` |
| Ingestion CSV/traceability/results | Canonical provenance | Durable ingestion root beneath `/var/lib/invomatch` |
| Export metadata and finalized projections | Canonical durable when produced | SQLite beneath durable state/export roots |
| Retained artifacts, exports, uploads | Canonical durable when produced/retained | Mounted filesystem state |
| Temp/log files | Reconstructable or operational | Not financial truth |
| Browser sessions and in-memory metrics | Ephemeral | Re-login/reset is acceptable |
| Images, source, static frontend build | Reconstructable deployment material | Rebuilt from audited commit |

## Backup and restore readiness audit

Operators have a bounded documented stop/quiesce, backup, clean restore, integrity verification, and restart path through `python -m invomatch.operations.pilot_state`. The repository claims only same-version, manually retained, quiesced controlled-pilot recovery. It does not claim online backup, continuous replication, HA, multi-region recovery, or enterprise disaster recovery.

## Operational procedure audit

`README.md` documents the canonical Compose start, stop, restart, quiesced backup, clean restore, restart, and integrity-verification commands. The served login flow, public `/health` and `/readiness`, and authenticated `/api/operations/release-identity` provide the remaining operator checks. No missing repository command makes the controlled pilot impossible to operate. Target-host provisioning, TLS termination, network restriction, real credential injection, and external backup destination selection remain environment actions.

## Final validation evidence

The closure branch must retain the established CI validation path rather than introduce a parallel framework. Required evidence is:

- focused EPIC 34 runtime, security, session, readiness, durability, restart, backup/restore, match persistence, and Match Detail tests;
- complete backend suite;
- contract, operational/recovery, and Scenario 15 regression packs;
- frontend ESLint and TypeScript/Vite production build;
- Python compilation and `git diff --check`;
- the existing real Compose gate, including build/start, health/readiness, authentication, deployed Scenario 15, queue/detail identity, routine recreation, backup/restore, integrity verification, build identity, and secret scans.

The final committed validation counts and CI run are recorded in the Draft PR and terminal handoff. A green closure-branch Compose run is required for the verdict below; no public deployment action is part of validation.

## Remaining environment go-live actions

The following are `ENVIRONMENT_GO_LIVE_ACTION`, not repository blockers:

- provision/select the controlled host or container runtime;
- restrict inbound access to approved pilot users/networks;
- configure the chosen hostname/DNS and terminate real TLS;
- inject actual non-demo pilot credentials and environment-specific release identity;
- select the allowed origin/network posture and external backup destination/retention;
- start the audited composition on the selected host and execute the operator health/readiness/login/identity checks.

These actions require a separately controlled target-environment launch process. This closure does not execute or authorize public deployment.

## Post-pilot enhancements

The following are `POST_PILOT_ENHANCEMENT`, not closure blockers: cloud orchestration, Kubernetes, autoscaling, HA, multi-region operation, enterprise SSO, managed secrets, centralized tracing, automated backup retention, online snapshots, general schema migrations, broad browser automation, commercial onboarding, billing, and analytics.

No repository-level `CLOSURE_BLOCKER` remains for a controlled pilot.

## Release and predecessor governance

EPIC 32 remains closed. This audit creates no tag, GitHub Release, release approval, manifest, version change, image publication, or environment promotion. Pilot validation is tied to the audited commit identity; any future formal release or promotion must follow the existing release-governance boundary.

EPIC 33 remains terminally closed. This audit confirms its backend-owned financial-truth and presentation-only UI/FTL invariants; it does not reopen or redesign them.

## Final verdicts

EPIC 34 has closed all acceptance-critical repository/runtime gaps for a controlled pilot. Repository and runtime-composition readiness is complete; environment-specific launch remains separate.

`EPIC_34_TERMINALLY_CLOSED`

`CONTROLLED_PILOT_GO_LIVE_REPOSITORY_READY`

This does not mean publicly deployed, production live, generally available, formally released, or customer-ready at scale. EPIC 34 stops here. Mini-EPIC 34.6 is not created and EPIC 35 is not started.
