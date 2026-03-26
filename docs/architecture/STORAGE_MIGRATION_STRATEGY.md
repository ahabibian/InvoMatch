# STORAGE MIGRATION STRATEGY — InvoMatch

## Purpose

Define deterministic schema evolution for RunStore.

Goals:

- zero corruption
- safe upgrades
- multi-worker startup safety
- forward-only evolution

---

## Schema Versioning

Schema version stored in:

schema_meta(schema_version INTEGER)

Rules:

- Every structural change bumps version
- Migration runs sequentially
- No downgrade support
- Partial migration must rollback

---

## Boot Migration Flow

1. open connection
2. read schema version
3. if outdated -> run migrations
4. verify final version

Startup must fail on incompatible version.

---

## Multi Worker Safety

Only one worker performs migration.

Others block on DB lock.

No race conditions allowed.

---

## Payload Evolution

Payload version separate from schema version.

Historical payloads must NOT be rewritten eagerly.

Lazy upgrade strategy preferred.

---

## SQLite -> Postgres Future

Migration steps must stay backend-agnostic.

No SQLite-specific assumptions in schema logic.

---

## Release Rule

No release allowed unless:

- contract tests pass
- concurrency tests pass
- migration test from previous version passes

Storage reliability is a trust boundary.