# Mini-EPIC 34.3 — Durable Pilot State and Operational Safety

## Boundary and baseline

Starting `main` is `d199fe1613c48fbf51aae6bc2d5a2de1ba1ab659`, containing merged Mini-EPIC 34.2 and `PILOT_RUNTIME_COMPOSITION_READY`. The duplicate gate found no canonical post-34.2 implementation combining configured match-store wiring, mounted restart proof, safe backup/restore, and restored-state validation. EPIC 32 and EPIC 33 remain closed. Mini-EPIC 34.4 is not executed here.

## Canonical state set and inventory

The single durable state set is `/var/lib/invomatch`, mounted as Compose volume `pilot_state`. Production validation rejects configured pilot paths outside it. `/tmp`, process memory, container logs, images, source, and frontend assets are not canonical business state.

| Surface | Effective pilot path | Classification / backup |
|---|---|---|
| Reconciliation runs | `/var/lib/invomatch/reconciliation_runs.sqlite3` | canonical / yes |
| Reviews | `/var/lib/invomatch/review_store.sqlite3` | canonical / yes |
| Match records | `/var/lib/invomatch/match_records.sqlite3` | canonical / yes |
| Audit and security audit | `/var/lib/invomatch/audit_events.sqlite3` | canonical evidence / yes |
| Input sessions | `/var/lib/invomatch/input_sessions.sqlite3` | canonical input evidence / yes |
| Ingestion CSV, traceability, result | `/var/lib/invomatch/ingestion_batches/` | canonical provenance / yes |
| Finalized projections | `/var/lib/invomatch/exports/finalized_projections.sqlite3` | canonical / yes |
| Export metadata | `/var/lib/invomatch/export_artifacts.sqlite3` | canonical when produced / yes |
| Export/artifact files | `/var/lib/invomatch/exports/` and `artifacts/` | canonical when produced / yes |
| Uploaded inputs | `/var/lib/invomatch/uploads/` | canonical when retained / yes |
| Feedback configuration | `/var/lib/invomatch/feedback_store.sqlite3` | currently no active pilot API consumer; included if present, no false active-use claim |
| Temp and logs | `tmp/`, `logs/` | reconstructable/ephemeral; copied if present, no truth claim |
| Browser sessions, metrics, stdout | process/container | ephemeral / no |

The complete mounted tree is the backup unit, preserving database-to-file relationships. Secret environment values, TLS keys, cookies, source, images, and build assets live outside it.

## Mandatory wiring corrections

Previously, importing `reconciliation.py` instantiated `output/reconciliation_match_records.sqlite3`, while application construction ignored the configured match path. The persistence factory now validates the SQLite backend, constructs `SqliteMatchRecordStore(settings.persistence.match_record_store_path)`, and injects it into every application reconciliation call. Import-time persistence is removed. Direct library/test callers retain a lazy convenience fallback; production/pilot application wiring cannot reach it. The configured ingestion batch root is also injected into `IngestionRunRuntimeAdapter`, eliminating its application-path fallback to `output/ingestion_batches`.

## Backup, restore, integrity, and schema posture

`python -m invomatch.operations.pilot_state` supplies bounded `backup`, `restore`, and `verify` commands. The operator stops services first, creating a controlled multi-SQLite quiescence window. Backup requires an existing state root and a new destination outside that root. It runs `PRAGMA integrity_check` before and after copying the full state set and records format version, UTC timestamp, application version, source commit, environment, source-root identity, included databases, file count, and SHA-256 for every file. It never silently overwrites a bundle.

Restore validates metadata, the complete file inventory and hashes, then SQLite integrity; it refuses a non-empty target and copies all-or-fails. Missing metadata/payload, removed or changed files, corruption, unsupported format, invalid destination, or unsafe overwrite fails closed. The current code-driven schemas initialize idempotently. Restore compatibility is asserted only for the same application version; no general migration framework is introduced.

Credentials, `INVOMATCH_SECURITY_SEED_TOKENS_JSON`, environment files, TLS keys, and in-memory sessions are excluded. Metadata records `secrets_included: false`, and CI scans for its temporary credential. Backups use an external host-mounted directory and manual operator retention.

## Deterministic restart and recovery proof

CI starts the real Nginx/private-Uvicorn Compose topology with a temporary non-demo admin credential. Through the authenticated ingestion API it creates batch `epic-34-3-durability`, invoice `INV-34-3`, payment `PAY-34-3`, EUR 125.50, and provenance reference `PILOT-34-3`. This materializes run identity/status/report, match identity/status/confidence, audit evidence, and ingestion files beneath the state root.

CI records the run ID, performs `docker compose down` without deleting the volume, recreates both containers, re-authenticates, and reads the identical run. It stops services, creates the quiesced external backup, deletes the active volume, restores to the clean replacement volume, restarts with startup repair enabled, re-authenticates, reads the same canonical run, and runs integrity verification. Database-referenced ingestion CSV paths and provenance files survive because both are within the restored set. Valid restored state remains readable and startup repair does not turn unresolved state into success.

Focused coverage proves configured store/batch wiring, reconstruction, metadata and artifact preservation, missing-state failure, overwrite rejection, missing-metadata rejection, hash-corruption rejection, integrity checking, and secret exclusion. Full backend, contract, operational/recovery, security/session, Scenario 15 compatibility, frontend lint/build, Python compilation, Compose durability, and whitespace checks remain required gates.

Operator start/stop/restart/backup/restore/verify commands are in `README.md`. Online snapshots, cloud storage, HA, distributed sessions, automatic retention, and schema migrations are outside this controlled pilot scope.

Mini-EPIC 34.4 remains the separate final deployed Scenario 15 proof across the full runtime network boundary. No public deployment occurs here.

## Verdict

`PILOT_DURABLE_STATE_READY`
