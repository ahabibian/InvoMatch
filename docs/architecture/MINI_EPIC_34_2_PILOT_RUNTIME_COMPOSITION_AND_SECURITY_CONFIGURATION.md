# Mini-EPIC 34.2 — Pilot Runtime Composition and Security Configuration

## Status

Starting baseline: `6ad4e95467c7dcc9f2309259735c78c9c10ece9b`

Primary verdict: `PILOT_RUNTIME_COMPOSITION_READY`

This Mini-EPIC composes and secures the pilot runtime. It does not complete Mini-EPIC 34.3 durability, backup, restore, or mounted-restart proof; it does not perform Mini-EPIC 34.4 deployed Scenario 15 validation; and it does not reopen EPIC 32 or EPIC 33.

## Architecture and duplicate gate

The baseline contains the merged Mini-EPIC 34.1 inspection and its `READY_FOR_PILOT_RUNTIME_IMPLEMENTATION` outcome. Repository-wide inspection found no newer same-origin frontend/backend composition, browser-session boundary, or equivalent 34.2 implementation. The implementation gate therefore permitted this bounded composition.

## Selected runtime topology

The canonical pilot topology is one externally visible same origin:

`HTTPS pilot origin → TLS ingress → Nginx static/proxy service → private Uvicorn/FastAPI backend`

Nginx serves the compiled Pilot UI at `/`, proxies `/api/*`, `/health`, and `/readiness` to `backend:8000`, and is the only service with a host port. The backend uses the existing `uvicorn invomatch.main:app --host 0.0.0.0 --port 8000` command and is exposed only to the internal Compose network.

`docker-compose.pilot.yml` is the single supported pilot composition. It builds both services, waits for backend readiness before the frontend starts, defines health checks, provides restart behavior, and prepares one named volume at `/var/lib/invomatch`.

The production frontend is the Vite `dist` artifact built in a Node 24 stage and served by Nginx. Vite development and preview servers are not part of the pilot topology.

## API origin and TLS model

Production frontend calls use relative `/api/...` URLs and `credentials: "same-origin"`. No browser-visible backend port or separate public API origin is required.

Backend CORS now reads an explicit `INVOMATCH_ALLOWED_ORIGINS` allow-list. Local/development defaults retain only localhost Vite origins. Production composition uses an empty CORS allow-list because requests are same-origin. Wildcards are rejected by startup validation.

Browser-facing pilot traffic is required to use HTTPS. TLS terminates at an external ingress/serving boundary; Nginx-to-Uvicorn traffic remains private HTTP. Local CI composition may use HTTP with `INVOMATCH_SESSION_COOKIE_SECURE=false`; staging/production default to secure cookies.

## Authentication and browser session model

Existing token authority and backend role/permission enforcement remain canonical. The browser-safe path is:

1. the operator enters an externally supplied pilot credential into the login surface;
2. `POST /api/auth/login` validates it through the existing `AuthenticationService` and `StaticTokenProvider`;
3. invalid, expired, revoked, or inactive identities are rejected;
4. the backend creates a cryptographically random opaque session identifier stored only in process memory;
5. the identifier is returned as `invomatch_session`, with `HttpOnly`, `SameSite=Strict`, path `/`, bounded `Max-Age`, and `Secure` in staging/production;
6. existing API security dependencies resolve the principal from the session when no Authorization header is present;
7. authorization remains backend-owned;
8. `POST /api/auth/logout` revokes the session and deletes the cookie.

Bearer headers remain supported for controlled non-browser API clients. The frontend no longer references `VITE_API_AUTH_TOKEN`, constructs an Authorization header, stores credentials in localStorage, or retains the submitted credential after login.

The in-memory session store intentionally supports the selected single-backend pilot runtime. Sessions are lost on restart and users must sign in again; financial and audit truth remain in durable stores. Distributed session infrastructure is outside this pilot boundary.

## Fail-closed credential configuration

Known committed demo tokens default only in local, development, and test environments. Staging and production now default to empty credential configuration and fail startup validation when authentication is enabled without explicitly supplied credentials. They also reject the known `viewer-token`, `operator-token`, `admin-token`, and `inactive-token` values even if supplied explicitly.

The Compose file requires `INVOMATCH_SECURITY_SEED_TOKENS_JSON` through external environment interpolation. `pilot.env.example` deliberately leaves it empty. No real credential is committed, built into either image, or placed in frontend configuration.

## Pilot configuration profile

The Compose profile fixes:

- `INVOMATCH_ENV=production`;
- SQLite run/review/feedback/match/audit/input/export paths beneath `/var/lib/invomatch`;
- artifact, export, upload, temp, and log paths beneath the same prepared state root;
- startup validation, startup repair, runtime recovery, authentication, and security audit enabled;
- scheduler disabled;
- same-origin CORS posture;
- secure, expiring session cookie posture;
- INFO/structured logging posture;
- externally injected version, commit, branch, and validation identity.

The root `pilot_state` volume is a composition boundary only. Mini-EPIC 34.3 must reconcile every actual store with these configured paths and prove mounted restart, backup, restore, and integrity behavior.

## Readiness and health

`/health` remains lightweight. `/readiness` now verifies:

- startup repair produced a usable state;
- configured critical SQLite run/review/audit/input stores can be opened according to selected backends;
- artifact, export, upload, temp, and log directories exist and are writable.

A dependency or startup blocking failure returns HTTP 503 with `status: not_ready`, a bounded readiness reason, and non-secret dependency codes. Healthy readiness returns HTTP 200. The backend Compose health check uses this endpoint, and frontend startup waits for backend health.

## Logging boundary

Application startup configures the selected log level and emits a safe startup-complete event containing only environment and scheduler posture. Authentication denial logs only a bounded failure category. Readiness failures log bounded reason/dependency identifiers. Uvicorn continues to provide access and unexpected application error logging, while existing persistent security and operational audit evidence remains intact.

Logs do not intentionally include credentials, session cookies, environment secret values, uploaded documents, or financial payloads.

## Runtime versions and build identity

The selected pilot build path is:

- backend runtime: existing Python 3.11 slim image;
- frontend build: Node 24 with `npm ci` and committed `package-lock.json`;
- frontend serving: Nginx 1.27 Alpine;
- database: Python SQLite;
- orchestration: Docker Compose.

The profile injects existing release identity inputs (`INVOMATCH_APPLICATION_VERSION`, commit SHA, branch, and validation status). The protected existing operational release-identity endpoint remains authoritative. No release or `v0.1.0` change occurs.

## Scheduler posture

`PILOT_SCHEDULER_DISABLED_AND_NOT_REQUIRED`

The current interactive pilot UI/API path does not depend on a background scheduler, and the repository has no active scheduler loop to compose. The pilot profile explicitly disables it. Startup repair and request-driven behavior remain available. Later scheduler work must be separately justified.

## Frontend integration

The existing application is gated by backend session bootstrap. Unauthenticated users receive the narrow Pilot Login surface. Authenticated users retain the existing EPIC 33 screens and backend-derived permissions. Sign-out invalidates the server session. Unauthorized, expired-session, permission, trust, and backend failure semantics remain distinct.

No general UI redesign or financial behavior change was introduced.

## Composition validation

The existing CI workflow now performs a real Docker Compose smoke test after backend, contract, operational, scenario, frontend lint, and frontend build validation. It:

1. injects a temporary non-demo CI credential and build identity;
2. validates Compose configuration;
3. builds and starts the Node/Nginx frontend plus Python/Uvicorn backend;
4. waits for dependency-aware service health;
5. retrieves the static UI through the public serving boundary;
6. retrieves `/health` and `/readiness` through Nginx;
7. logs in through `/api/auth/login`, retains the HttpOnly cookie, and accesses `/api/auth/session` through the same origin;
8. verifies the frontend artifact contains no `VITE_API_AUTH_TOKEN` reference;
9. tears down services and the disposable validation volume.

Docker is not installed in the local Windows execution environment used to author this boundary. Therefore local validation covers source/unit/process contracts, while the required real composition execution is provided by the Linux GitHub Actions runner. `PILOT_RUNTIME_COMPOSITION_READY` is valid only when that CI smoke step passes on the committed branch.

## Validation evidence

Focused tests cover:

- staging/production missing credentials fail closed;
- production rejects committed demo credentials;
- local development retains explicit convenience defaults;
- valid login creates an HttpOnly, strict, expiring session;
- production cookie posture includes `Secure`;
- invalid and inactive login rejection;
- logout revocation;
- session-backed protected API access and preserved authorization denial;
- explicit CORS allow-list behavior;
- non-2xx dependency readiness failure;
- absence of frontend bundled bearer-token configuration;
- private backend and persistent mount declarations.

Frontend ESLint and TypeScript/Vite production build remain required. Full backend, contract, operational, scenario, and real Compose smoke validation remain required in CI.

## Durable-state handoff to Mini-EPIC 34.3

Mini-EPIC 34.2 prepares `/var/lib/invomatch` and places all declared durable paths beneath it. It intentionally does not claim that every current service uses those settings. Mini-EPIC 34.3 must:

- inject the configured match-record store instead of the module default;
- reconcile feedback and export-artifact configuration with actual runtime wiring;
- prove every pilot-path database/artifact resides in the mounted state root;
- validate restart with preserved state;
- define and execute bounded backup, restore, and integrity procedures.

## Remaining Mini-EPIC 34.4 boundary

The CI composition smoke proves runtime assembly, static/API routing, readiness, and session bootstrap. It is not the final deployed Scenario 15 proof. Mini-EPIC 34.4 must validate the real pilot workflow through the composed network boundary after 34.3 durability is complete, including restart and failure evidence in a pilot-like deployed environment.

## Final decision

The repository now provides one reproducible same-origin pilot topology, production static serving, private backend routing, fail-closed production credentials, browser-safe session delivery, explicit pilot configuration, dependency-aware readiness, bounded safe logging, build identity, and a prepared state mount.

`PILOT_RUNTIME_COMPOSITION_READY`

