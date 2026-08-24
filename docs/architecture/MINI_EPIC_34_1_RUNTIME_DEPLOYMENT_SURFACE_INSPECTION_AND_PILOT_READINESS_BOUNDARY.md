# Mini-EPIC 34.1 — Runtime & Deployment Surface Inspection and Pilot Readiness Boundary

## Status and verdict

Inspected `main`: `d1e83579da35fdd391d44cd3ec2584fa74e4a485`

Primary verdict: `READY_FOR_PILOT_RUNTIME_IMPLEMENTATION`

The existing architecture can support a controlled pilot through bounded runtime, security-configuration, persistence, and deployment-composition work. InvoMatch is not safe for a real pilot deployment unchanged. The gaps are implementation and operational-integration gaps, not a fundamental runtime architecture conflict.

Mini-EPIC 34.1 performs inspection and defines the readiness boundary only. It does not deploy InvoMatch, change production behavior, create infrastructure, implement persistence, reopen EPIC 32 or EPIC 33, or begin Mini-EPIC 34.2.

## Baseline and architecture gate

The inspected baseline is the merge of PR #46, **docs(epic-33): complete final audit and close epic**. The canonical terminal record `EPIC_33_PILOT_UI_FTL_DEMONSTRATION_FINAL_AUDIT_AND_CLOSURE.md` is present and records `EPIC_33_TERMINALLY_CLOSED`.

Repository-wide inspection found earlier deployment and runtime foundations, especially EPIC 18, EPIC 22–24, EPIC 25–28, `CONFIGURATION_MODEL.md`, `ENVIRONMENT_PROFILE_RULES.md`, `DOCKER_PACKAGING_GUIDE.md`, `DEPLOYMENT_CHECKLIST.md`, and the existing Dockerfile. Those records define important component-level architecture and are treated as predecessors.

No artifact defines the same EPIC 34 controlled-pilot readiness assessment, integrates the current EPIC 33 Pilot UI path into a deployment contract, or classifies the current repository gaps for a real pilot. The duplicate gate therefore permits this record. This record does not replace the earlier runtime architecture.

## Backend runtime

### Entry point and serving model

The production-intent application is the module-level `app = create_app()` in `src/invomatch/main.py`. The existing Docker command is:

`uvicorn invomatch.main:app --host 0.0.0.0 --port 8000`

The backend uses FastAPI and Uvicorn. `pyproject.toml` declares FastAPI, Uvicorn, Pydantic, pytest, and python-multipart. `PYTHONPATH=src` is set in the Docker image; an installed package can also resolve the module.

`create_app()` loads environment settings, validates them, constructs persistence/storage/runtime dependencies, runs startup repair when enabled, creates security and audit services, wires input/reconciliation/review/export/operations services, and registers the API routers. Tests may call `create_app()` with injected temporary stores and paths; that is a test construction surface, not a separate runtime.

There is no explicit FastAPI lifespan/shutdown handler. SQLite connections are opened within store operations rather than held as an application-global connection. The scheduler setting is loaded and exposed through runtime dependencies, but repository source does not start a scheduler loop or external worker. The current pilot request/read path does not require a separate worker, but any claimed automated recovery scheduling must first be wired and validated.

### Startup behavior

Startup configuration validation fails application construction on invalid numeric bounds, unsupported environment selections, empty auth token configuration, relative production output paths, production DEBUG logging, or disabled production authentication. Startup repair runs synchronously when enabled and feeds health/readiness state.

Validation presently checks configured values but does not comprehensively probe every database, filesystem mount, or downstream dependency for actual readability/writability before readiness is exposed.

## Frontend runtime

The Pilot UI is `ui/invomatch-ui`, built with React, TypeScript, and Vite using npm and `package-lock.json`.

- development: `npm run dev`
- validation/production build: `npm run build`
- build output: `ui/invomatch-ui/dist`
- local preview only: `npm run preview`
- API base: build-time `VITE_API_BASE_URL`, defaulting to same-origin
- bearer token: build-time `VITE_API_AUTH_TOKEN`, defaulting to empty

The frontend uses in-memory React view state rather than a browser URL router. Browser refresh returns to the initial upload view; there is no deep-link route requiring static-host fallback today. Static hosting, cache policy, TLS, reverse proxy, and deployment of `dist` are not defined. The backend Dockerfile does not build or serve the frontend.

The frontend is buildable but not deployable as a complete controlled-pilot runtime without an explicit static-host and API composition.

## API connectivity and network boundary

Pilot UI calls use `/api/...` product routes, including:

- `GET /api/auth/session`
- `GET /api/review/queue`
- `GET /api/review/matches/{match_id}/detail`
- the existing input, run, action, export, and operational routes used by other screens

The frontend may use same-origin requests or prepend `VITE_API_BASE_URL`. The backend CORS allow-list is hardcoded to `http://localhost:5173` and `http://127.0.0.1:5173`; it does not accept a configured deployed origin. Same-origin deployment could avoid CORS, but no reverse-proxy/static-host composition currently establishes that model.

The Docker backend listens on all interfaces at port 8000. Vite development normally serves port 5173. No public exposure is authorized by existing runtime assets. A controlled pilot should use pilot-restricted inbound access, TLS termination, and either one origin or an explicit narrow frontend-origin allow-list. No application runtime requires general outbound access after dependencies and artifacts are built.

## Persistence and durability

### Durable or production-capable foundations

The default configured run and review backends are SQLite. The application also creates SQLite-backed audit events, input sessions, finalized projections, and export-artifact metadata, with local filesystem artifact storage. SQLite stores create their schema on initialization and have restart-oriented tests.

Configured durable paths include:

- reconciliation runs
- review state, feedback embedded in review workflow, decisions, and review audit events
- security/operational audit events
- input sessions and ingestion batches
- finalized projections
- export artifact metadata and artifact files

When all databases and artifact roots are placed on a durable mounted filesystem, the core Scenario 15 review path can survive a process or machine restart. Startup repair and restart consistency tests provide useful recovery evidence.

### Ephemeral or incomplete runtime state

Operational metrics and recovery incident tracking are in memory and reset with the process. This is acceptable for live operational counters but must not be treated as durable audit truth. Persistent operational/security audit events use the SQLite audit repository.

### Wiring gaps

The centralized settings declare feedback and match-record store paths/backends, but `PersistenceDependencies` constructs only run, review, and audit stores. `main.py` calls `reconcile_and_save` without injecting a configured match-record store, so the function retains its module-level default `output/match_records.sqlite3`. That path bypasses the selected production environment and may be lost or written outside the mounted pilot data boundary.

The configured export-artifact database path is not used directly by `main.py`; runtime metadata is instead placed beneath the resolved artifact/export root. That can remain durable if the entire root is mounted, but configuration truth and actual placement must be reconciled before pilot launch.

Feedback repositories and standalone match-record stores exist, but their complete production wiring must be verified against the actual pilot workflow rather than inferred from configuration fields.

## Database/schema, backup, and recovery

SQLite schemas are created in code with `CREATE TABLE IF NOT EXISTS`; no Alembic or other versioned migration framework is present. This is workable for a single controlled pilot baseline if schema identity is fixed and upgrade behavior is explicitly constrained.

No canonical backup procedure, atomic multi-file snapshot process, restore rehearsal, retention policy, or database integrity check is implemented for the full set of SQLite files plus artifact directories. Restart tests prove application-level reload and repair behavior, not backup/restore operability.

Before a real pilot, operators need a bounded backup/restore procedure that treats the related SQLite databases and filesystem artifacts as one runtime state set. Enterprise disaster recovery is not required.

## Configuration inventory

Configuration is centralized in `src/invomatch/config` and loaded from `INVOMATCH_*` environment variables. `.env.example` documents local persistence, storage, runtime, observability, upload, scheduler, feature flags, and release metadata.

Required pilot configuration includes:

- explicit `INVOMATCH_ENV` (`staging` or `production` posture);
- all durable database and storage paths, resolved inside the mounted state boundary;
- run/review backend selections fixed to SQLite;
- startup validation/repair and recovery settings;
- scheduler posture explicitly selected;
- non-debug logging and metrics/audit posture;
- authentication and security audit settings;
- release/build identity metadata;
- deployed frontend API/origin configuration.

Optional/tunable non-secret values include leases, retry budget, timeouts, scan limits, upload limits, log level, and feature flags.

The current `.env.example` is local-development oriented. It omits the security configuration variables and frontend deployment variables needed to construct a safe pilot profile. Production defaults select absolute `/var/lib/invomatch`, `/var/log/invomatch`, and `/tmp/invomatch` roots, but the Dockerfile creates `/app/output/...` directories instead. The image and configuration documentation are therefore not yet one reproducible runtime contract.

## Secrets and authentication

Bearer-token authentication and role-based authorization are active by default. Roles include viewer, operator, and admin, with backend permission enforcement. `/api/auth/session` resolves the active backend principal and frontend permission context. Security events are persisted when security audit is enabled.

The token provider is configured from `INVOMATCH_SECURITY_SEED_TOKENS_JSON`. However, the loader supplies committed demonstration tokens (`viewer-token`, `operator-token`, `admin-token`, and `inactive-token`) when the variable is absent. Production startup checks only that the resulting token JSON is non-empty, so those known defaults can satisfy production validation. This is unsafe for a pilot.

`VITE_API_AUTH_TOKEN` is also unsuitable as a pilot secret mechanism: Vite embeds build-time values in browser JavaScript, making the token visible to every client that receives the bundle. It is useful only for controlled local development/testing. The Pilot UI has no login/token-exchange mechanism.

Pilot launch requires externally supplied, non-default credentials and a browser-safe authentication delivery model. A narrowly scoped same-origin session or operator-provided runtime credential flow is sufficient; enterprise SSO is not required. Secrets must not be committed, built into the frontend, printed in logs, or placed in image layers.

No database passwords, signing keys, third-party credentials, or encryption keys are required by the current SQLite/local-only architecture. TLS private material belongs at the serving/proxy boundary, not in source.

## Health, readiness, and release identity

Public `GET /health` and `GET /readiness` endpoints exist. They expose startup-repair outcomes, unresolved mismatches, skipped repair counts, and a ready/not-ready body state. Protected operational endpoints expose metrics, health summary, alerts, audit events, and release identity.

Limitations:

- readiness does not comprehensively test all configured SQLite files, mounted storage paths, or frontend/backend connectivity;
- the readiness route returns a JSON state but does not set a non-2xx status when not ready;
- when startup-repair result is unavailable, the endpoints report an available/ready posture with `startup_result_unavailable` rather than failing closed;
- health does not prove authentication configuration is safe or that the frontend is available.

A controlled pilot needs a dependency-aware readiness contract suitable for an operator or process supervisor. Liveness may remain lightweight.

## Logging and operational visibility

Uvicorn supplies process/access/error logging, and the application has persistent audit events, startup repair results, operational metrics, alerts, and correlation identifiers for selected recovery/audit flows.

The observability settings model includes log level, structured logging, runtime-event logging, and startup-report logging, but repository source does not configure a general application logger or consistently emit request, storage, and startup events according to those flags. Durable audit events are stronger than the general log implementation.

Before pilot launch, operators need a minimal logging contract covering startup outcome, request/endpoint failures, storage errors, authentication/authorization failures, and correlation identifiers without recording tokens or financial payloads. A hosted telemetry platform is not required.

## Deployment and release assets

### Existing deployment assets

- `Dockerfile`: backend-only Python 3.11 image, installs the project, exposes port 8000, and starts Uvicorn.
- `.dockerignore`: excludes source-control metadata, local outputs, virtual environments, caches, sample data, frontend dependencies, and frontend build output.
- `.env.example`: local/development configuration example, incomplete for secure deployed operation.
- `DOCKER_PACKAGING_GUIDE.md`, `DEPLOYMENT_CHECKLIST.md`, and EPIC 24 records: production-intent architecture and checklists.
- CI: Python 3.14 validation plus Node 24/npm frontend lint and build.

No Compose file, frontend image/static-host configuration, reverse proxy, service definition, deployment workflow, cloud configuration, infrastructure-as-code, or rollback/backup script exists. The Dockerfile uses unpinned backend dependency resolution, copies the full repository after installation, runs with the image's default root user, and does not declare a durable volume. It is a useful backend packaging foundation, not a complete reproducible pilot deployment.

### EPIC 32 release relationship

GitHub Release `v0.1.0` is published for approved source SHA `6c4b3c3e35798de945a3219bbd419d4f6e41d8b7`. The release has no attached assets. Its canonical manifest describes a deterministic source tar materialized on demand, not an attached runnable package, and explicitly records that deployment configuration is not defined.

The release does not contain a frontend `dist`, container image, dependency bundle, environment profile, secret material, or deployed state. It is release-governance/source identity evidence, not a pilot runtime distribution. EPIC 34 must build deployment artifacts from an explicitly selected current source revision or define a later runtime package identity without reopening or changing the v0.1.0 decision.

## Runtime versions

- Backend project requirement: Python `>=3.11`.
- Existing Docker runtime: Python 3.11 slim.
- Current CI validation: Python 3.14.
- Frontend CI: Node 24 with npm and `package-lock.json`.
- Frontend dependencies: React 19, TypeScript 6, Vite 8 as locked by npm.
- Database: SQLite through the Python standard library; no external database server version is required.

Mini-EPIC 34.2 should select one supported pilot build/runtime combination rather than add a platform matrix. Python 3.11 in the existing image and Node 24 for a locked frontend build are the clearest repository-backed starting points, with CI remaining the compatibility check.

## Failure and restart behavior

- Invalid selected environment, unsupported stores, invalid runtime bounds, empty effective auth configuration, relative production paths, or production DEBUG posture fail application construction.
- Process restart reloads configured SQLite-backed run/review/input/audit/finalized/export state and executes startup repair.
- Machine or deployment restart preserves data only if every used SQLite path and artifact directory is on durable storage; current packaging does not enforce that composition.
- The current module-default match-record path can silently fall outside the intended durable production mount.
- Frontend restart loses only browser navigation/selection state; backend truth remains authoritative.
- Backend unavailability and explicit API failure states are displayed as technical failures, not financial success.
- Operational in-memory metrics reset on restart; persistent audit history does not.
- There is no verified backup restore, deployed rollback, or full runtime restart rehearsal.

## Runtime readiness matrix

| Area | Current State | Pilot Suitability | Gap Classification | Next Action |
| --- | --- | --- | --- | --- |
| Backend runtime | Real FastAPI/Uvicorn entry point and backend Dockerfile | Strong foundation, not fully composed | `PILOT_REQUIRED` | Fix image/config alignment, choose runtime profile, add lifecycle/operator contract |
| Frontend runtime | Vite build produces static `dist`; no production host | Cannot be served as a complete pilot today | `PILOT_BLOCKER` | Add bounded static hosting/reverse-proxy composition |
| API connectivity | Same-origin capable; build-time API URL; localhost-only CORS | Local works, deployed origin undefined | `PILOT_BLOCKER` | Select same-origin or configurable allow-list and validate connectivity |
| Persistence | Core SQLite and filesystem stores exist; match-record wiring bypasses config | Durable basis exists, state set not consistently composed | `PILOT_BLOCKER` | Inject all configured stores and mount one explicit durable state boundary |
| Configuration | Typed environment loader and fail-fast rules | Substantial, but pilot profile/image paths incomplete | `PILOT_REQUIRED` | Define one externalized pilot profile and validate actual paths/dependencies |
| Secrets | Environment token JSON supported; known defaults and browser build token remain | Unsafe unchanged | `PILOT_BLOCKER` | Reject demo tokens outside local/test and use browser-safe credential delivery |
| Authentication | Backend bearer auth, roles, permissions, audit, auth-session endpoint | Backend suitable; frontend credential delivery unsuitable | `PILOT_BLOCKER` | Establish controlled pilot session/credential flow without bundle secrets |
| Health/readiness | Public endpoints plus startup-repair state and protected operations APIs | Useful but insufficient for orchestration/operator readiness | `PILOT_REQUIRED` | Add dependency-aware readiness and non-2xx not-ready behavior |
| Logging | Uvicorn logs plus persistent security/operational audit | Partial operator visibility | `PILOT_REQUIRED` | Wire minimal safe structured startup/request/storage failure logging |
| Deployment packaging | Backend Dockerfile only; unpinned deps; no frontend/runtime composition | Not a repeatable full pilot package | `PILOT_BLOCKER` | Build one bounded frontend+backend composition with durable mounts |
| Runtime versions | Python >=3.11, Docker 3.11, CI Python 3.14/Node 24 | Sufficient evidence, not declared as one pilot stack | `PILOT_REQUIRED` | Pin/document one supported pilot build and runtime stack |
| Network exposure | Backend 8000; local Vite 5173; no TLS/restricted ingress definition | Local only | `PILOT_REQUIRED` | Define pilot-restricted TLS ingress and required ports/origins |
| Restart/recovery | SQLite reload, startup repair, strong restart tests; no mounted-state rehearsal/backup | Application foundation exists | `PILOT_BLOCKER` | Validate restart on real mounted state and establish backup/restore procedure |

## Gap classification

### `PILOT_BLOCKER`

These gaps prevent a safe or truthful pilot today but can be resolved within the existing architecture:

1. No deployed frontend/static-host plus backend composition exists.
2. Deployed API origin/CORS behavior is not configured or validated.
3. Known default bearer tokens can satisfy production configuration, and a Vite build token would expose a shared secret to clients.
4. The browser lacks a pilot-safe authentication delivery/session mechanism.
5. Not all pilot state follows the centralized durable path; the match-record default can escape the production mount.
6. No deployment artifact enforces durable mounts for the complete SQLite/artifact state set.
7. No real mounted-state restart and backup/restore validation exists.
8. Scenario 15 has repository integration evidence but has not been executed against an actually deployed frontend/backend runtime.

### `PILOT_REQUIRED`

1. Align Docker runtime paths and one externalized pilot configuration profile.
2. Make readiness dependency-aware and fail with an operator-usable status.
3. Wire safe startup/request/storage/auth failure logging to the existing observability/audit posture.
4. Select and document one Python/Node/npm pilot build/runtime stack and improve dependency reproducibility.
5. Define pilot-restricted TLS/network exposure and operator access.
6. Decide scheduler posture explicitly; do not claim background recovery scheduling unless it is wired.
7. Reconcile configured feedback/export/match storage fields with actual runtime wiring.
8. Define a bounded schema baseline plus backup, restore, and integrity-check procedure.
9. Inject current build/release identity into the deployed runtime.

### `POST_PILOT_ENHANCEMENT`

- Kubernetes, autoscaling, multi-region or zero-downtime deployment;
- managed enterprise secrets platforms or enterprise SSO;
- a remote database migration where single-instance SQLite remains adequate;
- high-availability backup automation and advanced disaster recovery;
- centralized log aggregation, tracing, and extensive telemetry dashboards;
- broad browser/platform matrices and full end-to-end automation for every screen;
- public internet exposure, commercial onboarding, billing, and general SaaS productionization.

## Minimum remaining EPIC 34 sequence

### Mini-EPIC 34.2 — Pilot Runtime Composition and Security Configuration

Create the smallest reproducible frontend+backend serving composition. Select one origin/network model, externalize a safe pilot configuration, remove acceptance of demonstration credentials outside local/test, establish browser-safe authentication delivery, align image paths, and expose operator-usable health. Include no cloud-specific deployment unless selected separately.

### Mini-EPIC 34.3 — Durable Pilot State and Operational Safety

Route every pilot-path store through centralized configuration, enforce one mounted durable state set, establish schema identity plus backup/restore/integrity procedures, verify restart behavior, and wire minimal safe logging. This boundary must specifically eliminate the module-default match-record path.

### Mini-EPIC 34.4 — Deployed End-to-End Pilot Validation

Build and run the real composed runtime in an isolated pilot-like environment. Validate frontend access, authentication, health/readiness, Scenario 15 through real network boundaries, durable restart, failure semantics, backup/restore, and release/build identity. Do not rely solely on FastAPI TestClient or Vite compilation.

### Mini-EPIC 34.5 — Pilot Go-Live Readiness and EPIC 34 Closure

Audit the deployed evidence, remaining blocker state, operator procedure, restricted exposure, rollback/recovery posture, and go-live decision. Close EPIC 34 only if all `PILOT_BLOCKER` items are resolved.

This four-step continuation is justified by distinct mutation and evidence boundaries: runtime/security composition, durable-state safety, deployed execution, and final decision. Combining them would obscure failure ownership. No additional phase is currently justified.

## Closure statement

InvoMatch already contains the product architecture and core runtime components needed for a controlled pilot. It requires bounded integration and operational safety work, not a new financial, frontend, or deployment architecture.

`READY_FOR_PILOT_RUNTIME_IMPLEMENTATION`

Mini-EPIC 34.2 may begin only as the separately controlled runtime-composition and security-configuration boundary defined above.

