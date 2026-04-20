# Environment Profile Rules

## 1. Purpose

This document defines the behavior of each supported runtime environment.

The goal is to guarantee deterministic separation between local, development, test, staging, and production execution.

---

## 2. Supported Environments

Supported environment values:

- local
- development
- test
- staging
- production

Any other value is invalid.

---

## 3. Global Rules

All environments must obey the following rules:

- each environment must use isolated persistence paths
- each environment must use isolated storage roots
- startup behavior must be explicit
- scheduler behavior must be explicit
- startup validation must run unless explicitly disabled for controlled tests
- environment selection must not depend on code edits

---

## 4. Local Environment

Purpose:

- developer-controlled local execution

Allowed behavior:

- sqlite allowed
- local filesystem storage allowed
- relative output paths allowed
- verbose logging allowed
- scheduler optional
- startup repair optional

Expected path model:

- output/local/

Risk posture:

- convenience-first but still deterministic

---

## 5. Development Environment

Purpose:

- stable developer execution closer to real runtime behavior

Allowed behavior:

- sqlite allowed
- environment-isolated directories required
- scheduler optional
- startup repair enabled by default
- debug logging allowed

Expected path model:

- output/development/

Risk posture:

- safer than local
- still developer-oriented

---

## 6. Test Environment

Purpose:

- isolated automated test execution

Required behavior:

- scheduler disabled by default
- deterministic test overrides allowed
- temporary or isolated sqlite paths only
- cleanup-safe directories only
- startup repair optional depending on test scope

Expected path model:

- output/test/
- temporary pytest-controlled directories when appropriate

Risk posture:

- maximum isolation
- deterministic reproducibility

---

## 7. Staging Environment

Purpose:

- production-like deployment validation

Required behavior:

- scheduler enabled
- startup repair enabled
- debug disabled
- persistence paths isolated
- artifact storage isolated
- startup validation enabled

Expected path model:

- output/staging/ or explicit mounted directories

Risk posture:

- production-like safety

---

## 8. Production Environment

Purpose:

- real deployment

Required behavior:

- scheduler enabled
- startup repair enabled
- startup validation enabled
- debug disabled
- structured logging enabled by default
- no implicit relative output paths
- explicit writable directories required
- safe bounded retry settings required

Expected path model examples:

- /var/lib/invomatch/
- /var/log/invomatch/
- /tmp/invomatch/

Risk posture:

- safety-first
- fail-fast
- no convenience shortcuts

---

## 9. Isolation Requirements

The following resources must be isolated per environment:

- run store
- review store
- feedback store
- match record store
- export artifact repository
- artifact content storage
- input session repository
- ingestion batch root
- temp files
- logs

No path may be shared across environments.

---

## 10. Forbidden Behaviors

The following are forbidden:

- production using local output paths by accident
- test reusing development persistence
- staging sharing production storage roots
- scheduler silently running in test
- startup repair silently disabled in production
- environment selection hidden inside code

---

## 11. Validation Requirement

Environment profile compatibility must be validated at startup.

Validation must reject:

- invalid environment name
- path collisions across logical subsystems
- unsafe production defaults
- scheduler-invalid environment combinations
- repair-invalid environment combinations

---

## 12. Design Consequence

Environment is not only a label.

Environment is a policy boundary that affects:

- defaults
- startup rules
- path safety
- runtime safety
- deployability