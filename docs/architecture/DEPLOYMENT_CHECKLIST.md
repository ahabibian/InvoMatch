# Deployment Checklist

## 1. Purpose

This checklist defines the minimum conditions required before deploying InvoMatch into staging or production-like environments.

---

## 2. Configuration Checklist

- environment value is explicitly set
- configuration loads successfully
- configuration validation passes
- no unsafe defaults remain active
- feature flags are explicitly understood

---

## 3. Persistence Checklist

- run store path is valid
- review store path is valid
- feedback store path is valid
- match record store path is valid
- export artifact repository path is valid
- input session repository path is valid

---

## 4. Storage Checklist

- artifact root path exists or is creatable
- upload root path exists or is creatable
- temp directory exists or is creatable
- log directory exists or is creatable
- writable access is confirmed

---

## 5. Runtime Checklist

- lease_seconds validated
- retry_budget validated
- stuck_run_timeout_seconds validated
- scheduler behavior validated
- startup repair behavior validated
- startup validation enabled where required

---

## 6. Packaging Checklist

- Dockerfile present
- .dockerignore present
- .env.example updated
- startup command deterministic
- mounted persistence expectations documented

---

## 7. Regression Checklist

The following scenarios must remain green:

- Scenario 1 — Happy Path Full Flow
- Scenario 4 — Runtime Failure Terminalization
- Scenario 6 — Restart Recovery Consistency
- Scenario 7 — Startup Repair Visibility & Recovery Alignment

---

## 8. Closure Checklist

EPIC 24 is not closed unless:

- architecture docs exist
- implementation is complete
- tests exist
- required scenario reruns pass
- closure doc reflects real repo state