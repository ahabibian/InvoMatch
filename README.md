# InvoMatch

Deterministic invoice reconciliation backend.

## Layers
- API
- Services
- Domain
- Repositories

## Durable pilot operations

The canonical pilot state root is `/var/lib/invomatch`. Browser sessions and
container logs are ephemeral; databases, ingestion provenance, uploads, and
generated artifacts are durable. Stop the composition before backup.

```bash
docker compose -f docker-compose.pilot.yml up --detach --build --wait
docker compose -f docker-compose.pilot.yml down
docker compose -f docker-compose.pilot.yml up --detach --wait
docker compose -f docker-compose.pilot.yml stop

mkdir -p pilot-backups
docker compose -f docker-compose.pilot.yml run --rm --no-deps \
  -v "$PWD/pilot-backups:/backups" backend \
  python -m invomatch.operations.pilot_state backup \
    --state-root /var/lib/invomatch --bundle /backups/backup-YYYYMMDDTHHMMSSZ \
    --application-version 0.1.0 --source-commit-sha COMMIT --environment production

# Restore only into a clean/empty state volume.
docker compose -f docker-compose.pilot.yml run --rm --no-deps \
  -v "$PWD/pilot-backups:/backups:ro" backend \
  python -m invomatch.operations.pilot_state restore \
    --bundle /backups/backup-YYYYMMDDTHHMMSSZ --target-root /var/lib/invomatch
docker compose -f docker-compose.pilot.yml up --detach --wait
docker compose -f docker-compose.pilot.yml exec -T backend \
  python -m invomatch.operations.pilot_state verify --state-root /var/lib/invomatch
```

Backup refuses missing state or an existing destination, checks every SQLite
database, and hashes every file. Restore refuses a non-empty target. Credentials,
cookies, and environment files are excluded. Retention is operator-controlled;
restore is supported with the same application version.
