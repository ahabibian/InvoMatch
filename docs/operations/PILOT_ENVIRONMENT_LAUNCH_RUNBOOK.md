# Pilot Environment Launch Runbook

This runbook launches the already-audited controlled-pilot runtime on one Linux host. It does not provision a cloud platform or make the pilot public by itself. Replace `pilot.example.com` and `DEPLOYED_COMMIT_SHA`; never paste a real credential into this document, Git, shell arguments, or shared logs.

## 1. Host and network prerequisites

Use a supported, security-maintained Linux distribution with persistent disk capacity for Docker's `pilot_state` volume. Install Git, Docker Engine, Docker Compose plugin **2.24.4 or newer**, curl, jq, and Caddy. Provision a DNS A/AAAA record for the pilot hostname before certificate issuance.

Allow inbound `443/tcp`; allow `80/tcp` only for certificate issuance and HTTP-to-HTTPS redirect. Restrict SSH to approved administrator source IPs wherever feasible. Do not publicly allow `8080`, `8000`, database/state ports, or the Docker daemon. Confirm the host firewall rules with the operator's platform-native firewall tooling before launch.

The enforced path is:

`approved client -> HTTPS :443 -> host Caddy -> 127.0.0.1:8080 -> frontend Nginx -> private Compose backend -> /var/lib/invomatch`

## 2. Deploy the audited commit

```bash
git clone https://github.com/ahabibian/InvoMatch.git
cd InvoMatch
git fetch origin
git checkout main
git pull --ff-only
git rev-parse HEAD
test "$(git rev-parse HEAD)" = "DEPLOYED_COMMIT_SHA"
git status --short
```

Stop if the SHA differs or status is not empty. Do not deploy an unreviewed working tree.

## 3. Configure the host-local environment

Create the ignored file without placing the secret in command history:

```bash
umask 077
cp pilot.env.example .env.pilot
chmod 600 .env.pilot
${EDITOR:-vi} .env.pilot
```

Set `INVOMATCH_SECURITY_SEED_TOKENS_JSON` to externally supplied high-entropy, non-demo credential JSON. Keep `INVOMATCH_SESSION_COOKIE_SECURE=true`, set `INVOMATCH_RELEASE_COMMIT_SHA` to the verified SHA, and retain `main`, `controlled_pilot`, and the selected localhost port. The credential stays only in this host-local file; it is not a frontend build argument or part of pilot-state backups.

Define the exact Compose command once per shell:

```bash
export COMPOSE_FILE=docker-compose.pilot.yml:docker-compose.pilot-host.yml
export COMPOSE_ENV_FILES=.env.pilot
docker compose --env-file .env.pilot config --quiet
```

## 4. Start and verify the local boundary

```bash
docker compose --env-file .env.pilot up --detach --build --wait
docker compose --env-file .env.pilot ps
curl --fail --silent --show-error http://127.0.0.1:8080/health
curl --fail --silent --show-error http://127.0.0.1:8080/readiness
docker compose --env-file .env.pilot port frontend 8080
```

The last command must report `127.0.0.1:8080`. `docker compose ... ps` must show no host publication for backend port `8000`. If startup fails, inspect only bounded logs with `docker compose --env-file .env.pilot logs --tail 100 backend frontend`; do not publish logs containing environment values.

## 5. Terminate TLS on the host

After DNS resolves to the host, create `/etc/caddy/Caddyfile` with the real placeholder substitution:

```caddyfile
pilot.example.com {
    reverse_proxy 127.0.0.1:8080
}
```

Validate and reload using the installed service:

```bash
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
curl --fail --silent --show-error https://pilot.example.com/health
curl --fail --silent --show-error https://pilot.example.com/readiness
scripts/pilot_environment_smoke.sh https://pilot.example.com DEPLOYED_COMMIT_SHA
```

The script uses normal curl certificate and hostname validation and confirms unauthenticated session access is rejected. It never accepts a credential.

## 6. Login, release identity, and functional acceptance

Open `https://pilot.example.com`, enter the real pilot credential interactively, and do not record it. As an authorized operator, verify `/api/operations/release-identity` through the application/browser session reports the exact SHA, version `0.1.0`, branch `main`, environment `production`, and validation status `controlled_pilot`. If an operator exports the browser session to a temporary curl cookie jar using approved local tooling, run:

```bash
scripts/pilot_environment_smoke.sh https://pilot.example.com DEPLOYED_COMMIT_SHA /secure/local/path/pilot.cookies
```

Delete that ephemeral cookie jar after the check. Then perform the canonical acceptance sequence, reusing the existing Scenario 15 input and semantics documented in `docs/architecture/MINI_EPIC_34_4_DEPLOYED_END_TO_END_PILOT_VALIDATION.md`:

1. Confirm HTTPS is reachable and its certificate is valid for the expected hostname.
2. Confirm `/health` and `/readiness` succeed.
3. Confirm authenticated release identity matches the deployed SHA.
4. Login with the real credential and perform supported ingestion using the existing Scenario 15 fixture semantics.
5. Run reconciliation and confirm the deterministic ambiguous result reaches Review Queue.
6. Record the real backend `match_id`; open Match Detail using that exact identity.
7. Verify backend-owned confidence, reason, evidence, provenance, FTL fields, and expected unresolved/review-required state.
8. Logout, confirm the authenticated session is rejected, and login again.
9. Recreate the runtime with `docker compose --env-file .env.pilot down` followed by `docker compose --env-file .env.pilot up --detach --wait`.
10. Re-login and reread the same durable run, review, and match state.
11. Complete the quiesced backup, integrity check, clean-target restore rehearsal, and restored-state reread below before real pilot data where practical.

Do not alter scoring thresholds, reconciliation semantics, or the Scenario 15 fixture.

## 7. Quiesced backup and external retention

Canonical durable state beneath `/var/lib/invomatch` includes runs, review state, matches, audit/security evidence, input-session evidence, ingestion provenance, export metadata, finalized projections, and retained artifacts/uploads/exports. Browser sessions, containers, images, compiled frontend, in-memory metrics, and transient non-evidence logs are ephemeral or reconstructable.

```bash
mkdir -p pilot-backups
chmod 700 pilot-backups
docker compose --env-file .env.pilot stop
docker compose --env-file .env.pilot run --rm --no-deps \
  -v "$PWD/pilot-backups:/backups" backend \
  python -m invomatch.operations.pilot_state backup \
    --state-root /var/lib/invomatch \
    --bundle /backups/backup-YYYYMMDDTHHMMSSZ \
    --application-version 0.1.0 \
    --source-commit-sha DEPLOYED_COMMIT_SHA \
    --environment production
docker compose --env-file .env.pilot run --rm --no-deps backend \
  python -m invomatch.operations.pilot_state verify --state-root /var/lib/invomatch
docker compose --env-file .env.pilot up --detach --wait
```

Copy the completed bundle to an operator-controlled destination outside the application host. A bundle retained only on the pilot VM is not a sufficient final backup. Retention and external transport remain operator-controlled; `.env.pilot`, credentials, cookies, and TLS keys must not accompany the state bundle.

## 8. Same-version clean-target restore rehearsal

Use a maintenance window and the same audited application version. The restore tool intentionally refuses a non-empty target. Before real pilot data, rehearse against a disposable clean Compose volume; never delete the live volume merely to prove restoration.

```bash
export COMPOSE_PROJECT_NAME=invomatch-restore-rehearsal
export COMPOSE_FILE=docker-compose.pilot.yml:docker-compose.pilot-host.yml
export INVOMATCH_PILOT_PORT=18080
docker compose --env-file .env.pilot run --rm --no-deps \
  -v "$PWD/pilot-backups:/backups:ro" backend \
  python -m invomatch.operations.pilot_state restore \
    --bundle /backups/backup-YYYYMMDDTHHMMSSZ \
    --target-root /var/lib/invomatch
docker compose --env-file .env.pilot up --detach --wait
docker compose --env-file .env.pilot exec -T backend \
  python -m invomatch.operations.pilot_state verify --state-root /var/lib/invomatch
```

Browse `http://127.0.0.1:18080` only from the host or an approved SSH tunnel, log in again, and reread the restored run/review/match identities. When evidence is recorded, stop the rehearsal with `docker compose --env-file .env.pilot down`. Removing its disposable volume is a separate destructive operator decision. This procedure claims same-version, quiesced recovery only—not online recovery, HA, replication, point-in-time recovery, or zero RPO/RTO.
