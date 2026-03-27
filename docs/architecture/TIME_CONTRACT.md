# TIME CONTRACT — InvoMatch

## Purpose
Define strict, system-wide rules for handling timestamps.

This is a **non-negotiable invariant** across all layers:
- domain
- services
- persistence
- APIs

---

## Rules

### 1. Timezone
All timestamps MUST be timezone-aware.

- Required timezone: **UTC**
- Naive datetimes are strictly forbidden

✔ Correct:
datetime.now(UTC)

❌ Forbidden:
datetime.utcnow()

---

### 2. Serialization
All timestamps MUST be serialized as ISO-8601 strings.

Example:
2026-03-27T20:15:30.123456+00:00

---

### 3. Deserialization
All timestamps MUST be parsed using:

datetime.fromisoformat(value)

---

### 4. Storage
Persistence layers (SQLite, JSON, etc.) MUST store timestamps as TEXT (ISO-8601).

---

### 5. Domain Enforcement
All domain models MUST validate timezone-awareness.

Example:
- Pydantic validators must reject naive datetime

---

## Anti-Patterns (Forbidden)

- Mixing naive and aware datetimes
- Using datetime.utcnow()
- Storing timestamps as integers (epoch) without explicit contract
- Implicit timezone assumptions

---

## Rationale

Without strict time handling:
- ordering bugs appear
- distributed systems break
- audit trails become unreliable

This contract ensures:
- deterministic behavior
- consistent persistence
- safe future scaling (multi-region / async workers)

---

## Version

v1.0 — Initial contract (EPIC 4 foundation)